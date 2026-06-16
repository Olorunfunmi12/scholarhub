
import { Account } from '../types';

const ACCOUNT_KEY = 'scholarhub_account';
// Salt makes the token harder to guess from an email alone. There is no backend,
// so the token is intentionally derived (not random) from the email: this lets a
// returning client "activate" the same token on any device just by re-entering it.
const SALT = 'scholarhub-2026';

const hash = (input: string): string => {
  let h = 5381;
  for (let i = 0; i < input.length; i++) {
    h = (h * 33) ^ input.charCodeAt(i);
  }
  return Math.abs(h).toString(36).toUpperCase();
};

export const generateToken = (email: string): string => {
  const normalized = email.trim().toLowerCase();
  const part1 = hash(SALT + normalized).padStart(4, '0').slice(0, 4);
  const part2 = hash(normalized + SALT).padStart(4, '0').slice(0, 4);
  return `SH-${part1}-${part2}`;
};

export const verifyToken = (email: string, token: string): boolean => {
  return generateToken(email) === token.trim().toUpperCase();
};

export const registerAccount = (data: {
  name: string;
  email: string;
  country: string;
  degreeTarget: string;
}): Account => {
  const account: Account = {
    ...data,
    token: generateToken(data.email),
    createdAt: Date.now(),
  };
  localStorage.setItem(ACCOUNT_KEY, JSON.stringify(account));
  return account;
};

export const activateAccount = (email: string, token: string, name = 'Scholar'): Account | null => {
  if (!verifyToken(email, token)) return null;
  const account: Account = {
    name,
    email,
    country: '',
    degreeTarget: '',
    token: generateToken(email),
    createdAt: Date.now(),
  };
  localStorage.setItem(ACCOUNT_KEY, JSON.stringify(account));
  return account;
};

export const getAccount = (): Account | null => {
  const saved = localStorage.getItem(ACCOUNT_KEY);
  return saved ? JSON.parse(saved) : null;
};

export const signOut = (): void => {
  localStorage.removeItem(ACCOUNT_KEY);
};
