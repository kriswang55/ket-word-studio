/** Domain logic for the public demo. Roles select views; they are not accounts. */
export const STORAGE_KEY = 'ket-word-studio.demo.v1';
export const normalize = value => String(value).normalize('NFKC').toLowerCase().trim().replace(/\s+/gu, ' ');
const copy = value => JSON.parse(JSON.stringify(value));
const timestamp = () => new Date().toISOString();
const identifier = () => globalThis.crypto.randomUUID();
const fail = message => { throw new Error(message); };

export function matches(word, answer) {
  return [word.english, ...(word.aliases || [])].some(value => normalize(value) === normalize(answer));
}

function text(value, name, max) {
  if (typeof value !== 'string' || !value.trim() || value.trim().length > max || /[\x00-\x1f]/u.test(value)) {
    fail(`${name}需要 1–${max} 个字符，不能包含控制字符。`);
  }
  return value.trim();
}

function initialData(seed) {
  const words = seed.map(word => ({...copy(word), aliases: word.aliases || [], enabled: true}));
  const quizzes = [0, 1, 2].map(day => {
    const completed = new Date(Date.now() - (3 - day) * 86400000).toISOString();
    const answers = words.slice(day * 5, day * 5 + 5).map((word, i) => ({
      ...copy(word), answer: i < day + 2 ? word.english : '', correct: i < day + 2, answeredAt: completed,
    }));
    return {id: `sample-${day}`, mode: 'random', category: '全部主题', startedAt: completed,
      completedAt: completed, status: 'completed', sample: true, answers};
  }).filter(quiz => quiz.answers.length);
  return {version: 1, words, quizzes};
}

export class DemoStore {
  constructor(seed, storage) {
    if (!Array.isArray(seed) || !seed.length) fail('词库未加载。');
    this.seed = copy(seed);
    this.storage = storage;
    this.role = 'student';
    this.read();
  }

  read() {
    let raw;
    try { raw = this.storage.getItem(STORAGE_KEY); }
    catch { fail('浏览器禁止保存数据，请允许此网站使用本地存储后重试。'); }
    if (!raw) {
      this.data = initialData(this.seed);
      this.persist(this.data);
      return;
    }
    try {
      const data = JSON.parse(raw);
      if (data.version !== 1 || !Array.isArray(data.words) || !Array.isArray(data.quizzes)) throw new Error();
      const ids = new Set();
      for (const w of data.words) {
        if (typeof w.id !== 'string' || ids.has(w.id) || !w.id) throw new Error();
        ids.add(w.id);
        text(w.english, '英文', 100); text(w.chinese, '中文释义', 200); text(w.category, '主题', 40);
        if (typeof w.enabled !== 'boolean' || !Array.isArray(w.aliases) || w.aliases.some(a => typeof a !== 'string')) throw new Error();
      }
      for (const q of data.quizzes) {
        if (typeof q.id !== 'string' || !['active', 'completed', 'abandoned'].includes(q.status) ||
            !Array.isArray(q.answers) || !q.answers.length || !['random', 'review'].includes(q.mode)) throw new Error();
        for (const a of q.answers) {
          if (typeof a.id !== 'string' || typeof a.english !== 'string' || typeof a.chinese !== 'string' ||
              !Array.isArray(a.aliases) || !(a.answer === null || typeof a.answer === 'string') ||
              !(a.correct === null || typeof a.correct === 'boolean')) throw new Error();
        }
        if (q.status === 'completed' && q.answers.some(a => a.answer === null)) throw new Error();
      }
      if (data.quizzes.filter(q => q.status === 'active').length > 1) throw new Error();
      this.data = data;
    } catch { fail('本地演示数据无法读取。请使用“重置演示数据”恢复。'); }
  }

  persist(next) {
    try { this.storage.setItem(STORAGE_KEY, JSON.stringify(next)); }
    catch { fail('保存失败，浏览器存储空间不足或已禁用。此次修改未保存。'); }
    this.data = next;
  }

  mutate(action) {
    this.read();
    const next = copy(this.data);
    const result = action(next);
    this.persist(next);
    return copy(result ?? null);
  }

  requireRole(role) {
    if (this.role !== role) fail(role === 'teacher' ? '请切换到教师页面。' : '请切换到学生页面。');
  }

  switchRole(role) {
    if (!['student', 'teacher'].includes(role)) fail('请选择学生或教师页面。');
    this.role = role;
  }

  reset() { this.persist(initialData(this.seed)); }

  words({query = '', category = '全部主题', includeDisabled = false} = {}) {
    this.read();
    if (includeDisabled) this.requireRole('teacher');
    const q = normalize(query);
    return copy(this.data.words.filter(w => (includeDisabled || w.enabled) &&
      (category === '全部主题' || category === w.category) &&
      (!q || normalize(w.english + ' ' + w.chinese).includes(q))));
  }

  categories() { return [...new Set(this.words().map(w => w.category))]; }

  saveWord(input) {
    this.requireRole('teacher');
    const english = text(input.english, '英文', 100);
    const chinese = text(input.chinese, '中文释义', 200);
    const category = text(input.category, '主题', 40);
    if (!/[a-z]/u.test(normalize(english))) fail('英文词条需要包含英文字母。');
    if (!Array.isArray(input.aliases || []) || (input.aliases || []).length > 20) fail('其他可接受答案最多填写 20 个。');
    const aliases = [...new Set((input.aliases || []).map(a => text(a, '可接受答案', 100)))];
    if (typeof input.enabled !== 'boolean') fail('请选择词汇状态。');
    return this.mutate(data => {
      const existing = input.id ? data.words.find(w => w.id === input.id) : null;
      if (input.id && !existing) fail('词条不存在。');
      if (data.words.some(w => w.id !== input.id && normalize(w.english) === normalize(english))) fail('该英文词条已存在，请编辑已有词条。');
      const word = {id: existing?.id || identifier(), english, chinese, category, aliases, enabled: input.enabled};
      if (existing) Object.assign(existing, word); else data.words.push(word);
      return word;
    });
  }

  activeQuiz() {
    this.read();
    return copy(this.data.quizzes.find(q => q.status === 'active') || null);
  }

  startQuiz({count = 10, category = '全部主题', mode = 'random'} = {}) {
    this.requireRole('student');
    if (!Number.isInteger(count) || count < 1 || count > 500) fail('题数需要是 1–500 之间的整数。');
    if (!['random', 'review'].includes(mode)) fail('练习方式无效。');
    return this.mutate(data => {
      if (data.quizzes.some(q => q.status === 'active')) fail('请先完成或结束当前练习。');
      let pool = data.words.filter(w => w.enabled && (category === '全部主题' || w.category === category));
      if (mode === 'review') {
        const mistakes = new Set(this.mistakesFrom(data).map(w => w.id));
        pool = pool.filter(w => mistakes.has(w.id));
      }
      if (!pool.length) fail(mode === 'review' ? '当前主题没有启用的待复习词汇。' : '当前主题没有启用的词汇。');
      pool = [...pool];
      // Fisher–Yates produces a sample without repeating a word within one quiz.
      for (let i = pool.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pool[i], pool[j]] = [pool[j], pool[i]];
      }
      const quiz = {id: identifier(), mode, category, startedAt: timestamp(), completedAt: null,
        status: 'active', sample: false,
        answers: pool.slice(0, count).map(w => ({...copy(w), answer: null, correct: null, answeredAt: null}))};
      data.quizzes.push(quiz);
      return quiz;
    });
  }

  answer(id, index, answer) {
    this.requireRole('student');
    if (!Number.isInteger(index) || typeof answer !== 'string' || answer.length > 200) fail('答案格式无效或超过 200 个字符。');
    return this.mutate(data => {
      const quiz = data.quizzes.find(q => q.id === id);
      if (!quiz || !quiz.answers[index]) fail('题目不存在。');
      const question = quiz.answers[index];
      if (question.answer !== null) {
        if (question.answer !== answer.trim()) fail('这道题已提交，不能修改。');
        return {quiz, feedback: question};
      }
      if (quiz.status !== 'active' || quiz.answers.findIndex(a => a.answer === null) !== index) fail('请回答当前题目。');
      question.answer = answer.trim(); question.correct = matches(question, answer); question.answeredAt = timestamp();
      if (quiz.answers.every(a => a.answer !== null)) { quiz.status = 'completed'; quiz.completedAt = timestamp(); }
      return {quiz, feedback: question};
    });
  }

  abandon(id) {
    this.requireRole('student');
    this.mutate(data => {
      const quiz = data.quizzes.find(q => q.id === id && q.status === 'active');
      if (!quiz) fail('没有可结束的练习。');
      quiz.status = 'abandoned';
    });
  }

  records() {
    this.read();
    return copy(this.data.quizzes.filter(q => q.status === 'completed').reverse().map(q => {
      const correct = q.answers.filter(a => a.correct).length;
      return {...q, correct, total: q.answers.length, accuracy: Math.round(correct / q.answers.length * 1000) / 10};
    }));
  }

  detail(id) {
    const record = this.records().find(q => q.id === id);
    if (!record) fail('找不到已完成的练习。');
    return record;
  }

  mistakesFrom(data) {
    const words = new Map();
    for (const quiz of [...data.quizzes].reverse().filter(q => q.status === 'completed')) {
      for (const answer of quiz.answers) {
        if (!words.has(answer.id)) words.set(answer.id, {...answer, wrongCount: 0});
        if (!answer.correct) words.get(answer.id).wrongCount++;
      }
    }
    return [...words.values()].filter(w => !w.correct).sort((a,b) => b.wrongCount-a.wrongCount || a.english.localeCompare(b.english));
  }

  mistakes() { this.read(); return copy(this.mistakesFrom(this.data)); }

  summary() {
    const records = this.records();
    const total = records.reduce((n,q) => n+q.total, 0);
    const correct = records.reduce((n,q) => n+q.correct, 0);
    const scores = records.map(q => q.accuracy);
    return {attempts: records.length, questions: total, accuracy: total ? Math.round(correct/total*1000)/10 : 0,
      best: scores.length ? Math.max(...scores) : 0, worst: scores.length ? Math.min(...scores) : 0,
      average: scores.length ? Math.round(scores.reduce((a,b) => a+b,0)/scores.length*10)/10 : 0,
      mistakeCount: this.mistakes().length, wordCount: this.words().length,
      sampleCount: records.filter(q => q.sample).length, recent: records.slice(0,7)};
  }

  exportRecords(format, translate = value => value) {
    const records = this.records();
    if (format === 'json') return JSON.stringify({version: 1, exportedAt: timestamp(), records}, null, 2);
    if (format !== 'csv') fail('仅支持 JSON 或 CSV。');
    const cell = value => {
      let str = String(value);
      if (/^[\s]*[=+@-]/u.test(str)) str = "'"+str;
      return '"'+str.replaceAll('"','""')+'"';
    };
    return '\ufeff'+[['完成时间','主题','方式','题数','正确数','正确率(%)','来源'].map(translate),
      ...records.map(r => [r.completedAt,translate(r.category),translate(r.mode==='review'?'错题复习':'随机练习'),r.total,r.correct,r.accuracy,translate(r.sample?'示例':'本次演示')])]
      .map(row => row.map(cell).join(',')).join('\r\n');
  }
}
