export const LOCALES = ['en', 'zh-CN', 'zh-HK'];
export const LANGUAGE_KEY = 'ket-word-studio.language';
export const LANGUAGE_NAMES = {en: 'English', 'zh-CN': '简体中文', 'zh-HK': '繁体中文'};

export class Translator {
  constructor(catalogues = {}, locale = 'en') {
    this.catalogues = catalogues;
    this.locale = LOCALES.includes(locale) ? locale : 'en';
  }

  t(message, ...args) {
    const current = this.catalogues[this.locale] || {};
    let translated = current.messages?.[message] ?? current.categories?.[message];
    // Domain errors can contain a field name and length. Match the source template.
    if (translated === undefined && !args.length) {
      for (const [source, target] of Object.entries(current.messages || {})) {
        if (!source.includes('{0}')) continue;
        const pattern = source.split(/(\{\d+\})/u).map(part => /^\{\d+\}$/u.test(part)
          ? '([\\s\\S]+?)' : part.replace(/[.*+?^${}()|[\]\\]/gu, '\\$&')).join('');
        const match = message.match(new RegExp(`^${pattern}$`, 'u'));
        if (match) { translated = target; args = match.slice(1).map(value => current.messages?.[value] ?? value); break; }
      }
    }
    translated ??= this.catalogues.en?.messages?.[message] ?? message;
    return translated.replace(/\{(\d+)\}/gu, (whole, index) => args[index] ?? whole);
  }

  category(value) { return this.catalogues[this.locale]?.categories?.[value] ?? value; }
  meaning(value) { return this.catalogues[this.locale]?.prompts?.[value] ?? value; }

  select(locale, storage) {
    if (!LOCALES.includes(locale)) throw new Error('Unsupported locale');
    this.locale = locale;
    try { storage?.setItem(LANGUAGE_KEY, locale); return true; } catch { return false; }
  }
}

export const i18n = new Translator();
export const t = (message, ...args) => i18n.t(message, ...args);
export const cat = value => i18n.category(value);
export const meaning = value => i18n.meaning(value);

export async function loadLanguages(storage) {
  const entries = await Promise.all(LOCALES.map(async locale => {
    const response = await fetch(new URL(`./locales/${locale}.json`, import.meta.url));
    if (!response.ok) throw new Error('Language resources could not be loaded. Refresh to retry.');
    return [locale, await response.json()];
  }));
  i18n.catalogues = Object.fromEntries(entries);
  let locale;
  try { locale = storage.getItem(LANGUAGE_KEY); } catch { /* The demo reports storage errors separately. */ }
  i18n.locale = LOCALES.includes(locale) ? locale : 'en';
}
