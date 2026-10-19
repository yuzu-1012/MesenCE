using Mesen.Config;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Xml;

namespace Mesen.Localization
{
	class ResourceHelper
	{
		private const string DefaultLanguage = "en";

		private static XmlDocument _resources = new XmlDocument();

		private static Dictionary<Enum, string> _enumLabelCache = new();
		private static Dictionary<string, string> _viewLabelCache = new();
		private static Dictionary<string, string> _messageCache = new();

		public static void LoadResources(MesenLanguage language)
		{
			try {
				_messageCache.Clear();
				_enumLabelCache.Clear();
				_viewLabelCache.Clear();

				string code = GetResourceCode(language);

				XmlDocument? defaultResources = LoadEmbedded(DefaultLanguage);
				if(defaultResources == null) {
					Debug.WriteLine("Missing embedded default localization resources.");
					return;
				}

				_resources = defaultResources;
				Dictionary<string, Type> enumTypes = GetEnumTypes();
				Apply(defaultResources, false, enumTypes);

				if(code != DefaultLanguage) {
					Apply(LoadEmbedded(code), true, enumTypes);
				}

				//Allow translators to override the embedded translation without rebuilding
				Apply(LoadExternal(code), true, enumTypes);
			} catch(Exception ex) {
				Debug.WriteLine("Failed to load localization resources: " + ex.Message);
			}
		}

		public static void LoadResources()
		{
			LoadResources(MesenLanguage.Auto);
		}

		private static string GetResourceCode(MesenLanguage language)
		{
			switch(language) {
				case MesenLanguage.English:
					return "en";

				case MesenLanguage.ChineseSimplified:
					return "zh-CN";
			}

			string name = CultureInfo.CurrentUICulture.Name;
			if(name.StartsWith("zh", StringComparison.OrdinalIgnoreCase)) {
				if(name.Contains("Hant", StringComparison.OrdinalIgnoreCase) ||
					name.EndsWith("-TW", StringComparison.OrdinalIgnoreCase) ||
					name.EndsWith("-HK", StringComparison.OrdinalIgnoreCase) ||
					name.EndsWith("-MO", StringComparison.OrdinalIgnoreCase)) {
					return "zh-TW";
				}

				return "zh-CN";
			}

			return DefaultLanguage;
		}

		private static XmlDocument? LoadEmbedded(string code)
		{
			try {
				Assembly assembly = Assembly.GetExecutingAssembly();
				using Stream? stream = assembly.GetManifestResourceStream($"Mesen.Localization.resources.{code}.xml");
				if(stream == null) {
					return null;
				}

				using StreamReader reader = new(stream);
				XmlDocument doc = new();
				doc.LoadXml(reader.ReadToEnd());
				return doc;
			} catch(Exception ex) {
				Debug.WriteLine($"Failed to load embedded resources.{code}.xml: " + ex.Message);
				return null;
			}
		}

		private static XmlDocument? LoadExternal(string code)
		{
			try {
				string path = Path.Combine(ConfigManager.HomeFolder, "Localization", $"resources.{code}.xml");
				if(!File.Exists(path)) {
					return null;
				}

				XmlDocument doc = new();
				doc.Load(path);
				return doc;
			} catch(Exception ex) {
				Debug.WriteLine("Failed to load external localization file: " + ex.Message);
				return null;
			}
		}

		private static Dictionary<string, Type> GetEnumTypes()
		{
#pragma warning disable IL2026 // Members annotated with 'RequiresUnreferencedCodeAttribute' require dynamic access otherwise can break functionality when trimming application code
			return Assembly.GetExecutingAssembly().GetTypes().Where(t => t.IsEnum).ToDictionary(t => t.Name);
#pragma warning restore IL2026
		}

		private static void Apply(XmlDocument? doc, bool overwrite, Dictionary<string, Type> enumTypes)
		{
			if(doc == null) {
				return;
			}

			foreach(XmlNode node in doc.SelectNodes("/Resources/Messages/Message")!) {
				_messageCache[node.Attributes!["ID"]!.Value] = node.InnerText;
			}

			foreach(XmlNode node in doc.SelectNodes("/Resources/Enums/Enum")!) {
				string enumName = node.Attributes!["ID"]!.Value;
				if(!enumTypes.TryGetValue(enumName, out Type? enumType)) {
					if(overwrite) {
						//Ignore unknown enum types in translation files so a partial translation cannot break startup
						continue;
					}

					throw new Exception("Unknown enum type: " + enumName);
				}

				foreach(XmlNode enumNode in node.ChildNodes) {
					if(Enum.TryParse(enumType, enumNode.Attributes!["ID"]!.Value, out object? value) && value is Enum enumValue) {
						_enumLabelCache[enumValue] = enumNode.InnerText;
					}
				}
			}

			foreach(XmlNode node in doc.SelectNodes("/Resources/Forms/Form")!) {
				string viewName = node.Attributes!["ID"]!.Value;
				foreach(XmlNode formNode in node.ChildNodes) {
					if(formNode is XmlElement elem) {
						_viewLabelCache[viewName + "_" + elem.Attributes!["ID"]!.Value] = elem.InnerText;
					}
				}
			}
		}

		public static string GetMessage(string id, params object[] args)
		{
			if(_messageCache.TryGetValue(id, out string? text)) {
				return string.Format(text, args);
			} else {
				return "[[" + id + "]]";
			}
		}

		public static string GetEnumText(Enum e)
		{
			if(_enumLabelCache.TryGetValue(e, out string? text)) {
				return text;
			} else {
				return "[[" + e.ToString() + "]]";
			}
		}

		public static Enum[] GetEnumValues(Type t)
		{
			List<Enum> values = new List<Enum>();
			XmlNode? node = _resources.SelectSingleNode("/Resources/Enums/Enum[@ID='" + t.Name + "']");
			if(node?.Attributes!["ID"]!.Value == t.Name) {
				foreach(XmlNode enumNode in node.ChildNodes) {
					if(Enum.TryParse(t, enumNode.Attributes!["ID"]!.Value, out object? value) && value != null) {
						values.Add((Enum)value);
					}
				}
			}
			return values.ToArray();
		}

		public static string GetViewLabel(string view, string control)
		{
			if(_viewLabelCache.TryGetValue(view + "_" + control, out string? text)) {
				return text;
			} else {
				return $"[{view}:{control}]";
			}
		}
	}
}
