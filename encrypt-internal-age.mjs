#!/usr/bin/env node
// Encrypt ../INTERNAL.md as a standard age v1 X25519 recipient file.
// No private key is stored here. The recipient public key is Stephen-held recovery infrastructure.

import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const RECIPIENT = 'age1cwzd4sm6weem96npvwvcf586f34agzcar2qgs2alkkr7ny9q3d3qxskwgw';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const workspace = path.resolve(__dirname, '..');
const inputPath = path.join(workspace, 'INTERNAL.md');
const outputPath = path.join(__dirname, 'INTERNAL.age');

function bech32Polymod(values) {
  const GENERATOR = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3];
  let chk = 1;
  for (const value of values) {
    const top = chk >> 25;
    chk = ((chk & 0x1ffffff) << 5) ^ value;
    for (let i = 0; i < 5; i++) {
      if ((top >> i) & 1) chk ^= GENERATOR[i];
    }
  }
  return chk;
}

function hrpExpand(hrp) {
  const out = [];
  for (const ch of hrp) out.push(ch.charCodeAt(0) >> 5);
  out.push(0);
  for (const ch of hrp) out.push(ch.charCodeAt(0) & 31);
  return out;
}

const CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l';
function bech32Decode(str) {
  if (str !== str.toLowerCase() && str !== str.toUpperCase()) throw new Error('mixed-case bech32 string');
  str = str.toLowerCase();
  const pos = str.lastIndexOf('1');
  if (pos < 1) throw new Error('invalid bech32 separator');
  const hrp = str.slice(0, pos);
  const data = [...str.slice(pos + 1)].map((ch) => {
    const idx = CHARSET.indexOf(ch);
    if (idx === -1) throw new Error(`invalid bech32 character: ${ch}`);
    return idx;
  });
  if (data.length < 6) throw new Error('bech32 data too short');
  if (bech32Polymod([...hrpExpand(hrp), ...data]) !== 1) throw new Error('bech32 checksum failed');
  return { hrp, data: data.slice(0, -6) };
}

function convertBits(data, fromBits, toBits, pad) {
  let acc = 0;
  let bits = 0;
  const ret = [];
  const maxv = (1 << toBits) - 1;
  const maxAcc = (1 << (fromBits + toBits - 1)) - 1;
  for (const value of data) {
    if (value < 0 || (value >> fromBits) !== 0) throw new Error('invalid bit group');
    acc = ((acc << fromBits) | value) & maxAcc;
    bits += fromBits;
    while (bits >= toBits) {
      bits -= toBits;
      ret.push((acc >> bits) & maxv);
    }
  }
  if (pad) {
    if (bits > 0) ret.push((acc << (toBits - bits)) & maxv);
  } else {
    if (bits >= fromBits) throw new Error('excess padding');
    if (((acc << (toBits - bits)) & maxv) !== 0) throw new Error('non-zero padding');
  }
  return Buffer.from(ret);
}

function decodeAgeRecipient(recipient) {
  const { hrp, data } = bech32Decode(recipient);
  if (hrp !== 'age') throw new Error(`unsupported age recipient HRP: ${hrp}`);
  const raw = convertBits(data, 5, 8, false);
  if (raw.length !== 32) throw new Error(`age X25519 recipient must decode to 32 bytes, got ${raw.length}`);
  return raw;
}

function rawX25519PublicKey(raw) {
  return crypto.createPublicKey({
    key: Buffer.concat([Buffer.from('302a300506032b656e032100', 'hex'), raw]),
    format: 'der',
    type: 'spki'
  });
}

function rawX25519PrivateKey(raw) {
  return crypto.createPrivateKey({
    key: Buffer.concat([Buffer.from('302e020100300506032b656e04220420', 'hex'), raw]),
    format: 'der',
    type: 'pkcs8'
  });
}

function b64(buf) {
  return Buffer.from(buf).toString('base64').replace(/=+$/g, '');
}

function wrap64(s) {
  return s.match(/.{1,64}/g)?.join('\n') + '\n';
}

function hkdf(ikm, salt, info) {
  return Buffer.from(crypto.hkdfSync('sha256', ikm, salt, info, 32));
}

function chachaSeal(key, nonce, plaintext) {
  const cipher = crypto.createCipheriv('chacha20-poly1305', key, nonce, { authTagLength: 16 });
  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  return Buffer.concat([ciphertext, cipher.getAuthTag()]);
}

function chachaOpen(key, nonce, ciphertextAndTag) {
  const tag = ciphertextAndTag.subarray(ciphertextAndTag.length - 16);
  const ciphertext = ciphertextAndTag.subarray(0, ciphertextAndTag.length - 16);
  const decipher = crypto.createDecipheriv('chacha20-poly1305', key, nonce, { authTagLength: 16 });
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(ciphertext), decipher.final()]);
}

function encryptAge(plaintext, recipientRaw) {
  const fileKey = crypto.randomBytes(16);
  const eph = crypto.generateKeyPairSync('x25519');
  const ephPubRaw = eph.publicKey.export({ format: 'der', type: 'spki' }).subarray(-32);
  const shared = crypto.diffieHellman({ privateKey: eph.privateKey, publicKey: rawX25519PublicKey(recipientRaw) });
  const wrapKey = hkdf(shared, Buffer.concat([ephPubRaw, recipientRaw]), 'age-encryption.org/v1/X25519');
  const wrappedFileKey = chachaSeal(wrapKey, Buffer.alloc(12), fileKey);

  let headerPrefix = 'age-encryption.org/v1\n';
  headerPrefix += `-> X25519 ${b64(ephPubRaw)}\n`;
  headerPrefix += wrap64(b64(wrappedFileKey));
  headerPrefix += '---';
  const headerKey = hkdf(fileKey, Buffer.alloc(0), 'header');
  const mac = crypto.createHmac('sha256', headerKey).update(headerPrefix).digest();
  const header = `${headerPrefix} ${b64(mac)}\n`;

  const payloadNonce = crypto.randomBytes(16);
  const payloadKey = hkdf(fileKey, payloadNonce, 'payload');
  const chunks = [];
  const chunkSize = 64 * 1024;
  const totalChunks = Math.max(1, Math.ceil(plaintext.length / chunkSize));
  for (let i = 0; i < totalChunks; i++) {
    const start = i * chunkSize;
    const chunk = plaintext.subarray(start, Math.min(start + chunkSize, plaintext.length));
    const nonce = Buffer.alloc(12);
    // First 11 bytes are a big-endian chunk counter. This file is tiny, so a 48-bit suffix is sufficient.
    nonce.writeUIntBE(i, 5, 6);
    nonce[11] = i === totalChunks - 1 ? 0x01 : 0x00;
    chunks.push(chachaSeal(payloadKey, nonce, chunk));
  }
  return Buffer.concat([Buffer.from(header, 'utf8'), payloadNonce, ...chunks]);
}

function selfTest() {
  const recipient = crypto.generateKeyPairSync('x25519');
  const recipientPubRaw = recipient.publicKey.export({ format: 'der', type: 'spki' }).subarray(-32);
  const plaintext = Buffer.from('age compatibility self-test\n');
  const encrypted = encryptAge(plaintext, recipientPubRaw);
  const headerEnd = encrypted.indexOf(Buffer.from('\n--- ')) + 1;
  if (headerEnd <= 0) throw new Error('self-test header parse failed');
  const headerLastNewline = encrypted.indexOf('\n', headerEnd + 4);
  const lines = encrypted.subarray(0, headerLastNewline + 1).toString('utf8').split('\n');
  const ephPubRaw = Buffer.from(lines[1].split(' ')[2], 'base64');
  const body = Buffer.from(lines[2], 'base64');
  const shared = crypto.diffieHellman({ privateKey: recipient.privateKey, publicKey: rawX25519PublicKey(ephPubRaw) });
  const wrapKey = hkdf(shared, Buffer.concat([ephPubRaw, recipientPubRaw]), 'age-encryption.org/v1/X25519');
  const fileKey = chachaOpen(wrapKey, Buffer.alloc(12), body);
  if (fileKey.length !== 16) throw new Error('self-test file key length failed');
  const payloadOffset = headerLastNewline + 1;
  const payloadNonce = encrypted.subarray(payloadOffset, payloadOffset + 16);
  const payloadKey = hkdf(fileKey, payloadNonce, 'payload');
  const payloadBody = encrypted.subarray(payloadOffset + 16);
  const nonce = Buffer.alloc(12);
  nonce[11] = 0x01;
  const opened = chachaOpen(payloadKey, nonce, payloadBody);
  if (!opened.equals(plaintext)) throw new Error('self-test payload decrypt failed');
}

selfTest();
const recipientRaw = decodeAgeRecipient(RECIPIENT);
const plaintext = fs.readFileSync(inputPath);
const encrypted = encryptAge(plaintext, recipientRaw);
fs.writeFileSync(outputPath, encrypted);
console.log(`Encrypted ${inputPath} -> ${outputPath}`);
console.log(`Recipient: ${RECIPIENT}`);
console.log(`Bytes: ${encrypted.length}`);
