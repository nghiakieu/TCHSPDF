/**
 * textSearch.ts
 * Thuật toán tìm kiếm linh động chuẩn tiếng Việt phong cách Listary:
 * - Bỏ dấu tiếng Việt (kể cả đ/Đ).
 * - Khớp cả cụm liền nhau.
 * - Khớp từng từ không cần đúng thứ tự.
 * - Chấp nhận sai chính tả / khớp mờ (fuzzy).
 */

const EXTRA_MAP: Record<string, string> = {
  'đ': 'd',
  'Đ': 'D',
};

export function stripDiacritics(text: string): string {
  if (!text) return '';
  let str = text;
  for (const [k, v] of Object.entries(EXTRA_MAP)) {
    str = str.replaceAll(k, v);
  }
  return str
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .normalize('NFC');
}

export function normalize(text: string): string {
  if (!text) return '';
  const clean = stripDiacritics(text).toLowerCase();
  return clean.replace(/\s+/g, ' ').trim();
}

export function tokenize(normalizedText: string): string[] {
  const matches = normalizedText.match(/[^\W_]+/gu);
  return matches ? Array.from(matches) : [];
}

function stringSimilarity(s1: string, s2: string): number {
  if (s1 === s2) return 1.0;
  if (s1.includes(s2) || s2.includes(s1)) return 0.92;
  const longer = s1.length > s2.length ? s1 : s2;
  const shorter = s1.length > s2.length ? s2 : s1;
  const longerLength = longer.length;
  if (longerLength === 0) return 1.0;

  // Levenshtein distance approximation for short tokens
  const costs: number[] = [];
  for (let i = 0; i <= s1.length; i++) {
    let lastValue = i;
    for (let j = 0; j <= s2.length; j++) {
      if (i === 0) {
        costs[j] = j;
      } else if (j > 0) {
        let newValue = costs[j - 1];
        if (s1.charAt(i - 1) !== s2.charAt(j - 1)) {
          newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
        }
        costs[j - 1] = lastValue;
        lastValue = newValue;
      }
    }
    if (i > 0) costs[s2.length] = lastValue;
  }
  return (longerLength - costs[s2.length]) / longerLength;
}

function bestTokenRatio(token: string, targetTokens: string[]): number {
  let best = 0.0;
  for (const t of targetTokens) {
    if (token === t) return 1.0;
    if (best < 0.92) {
      if (token.includes(t) || t.includes(token)) {
        best = Math.max(best, 0.92);
        continue;
      }
      const ratio = stringSimilarity(token, t);
      if (ratio > best) {
        best = ratio;
      }
    }
  }
  return best;
}

export function matchScore(query: string, ...fields: string[]): number {
  const queryNorm = normalize(query);
  if (!queryNorm) return 1.0;

  const combinedNorm = normalize(fields.filter(Boolean).join(' '));
  if (!combinedNorm) return 0.0;

  let score = 0.0;

  // Khớp cả cụm liền nhau
  if (combinedNorm.includes(queryNorm)) {
    score += 100.0;
    if (combinedNorm.startsWith(queryNorm)) {
      score += 20.0;
    }
  }

  const qTokens = tokenize(queryNorm);
  if (qTokens.length === 0) return score;

  const targetTokens = tokenize(combinedNorm);
  if (targetTokens.length === 0) return score;

  const perTokenScores = qTokens.map((tok) => bestTokenRatio(tok, targetTokens));
  const matched = perTokenScores.filter((r) => r >= 0.7);

  if (matched.length < qTokens.length) {
    return score;
  }

  score += matched.reduce((a, b) => a + b, 0) * 10.0;
  return score;
}
