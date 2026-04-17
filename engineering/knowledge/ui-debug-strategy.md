# UI変更のデバッグ戦略

## 問題

CLIで「ビルド成功」「サーバー起動OK」と出ても、実際のUIでは全く反映されていないことが頻発する。原因はキャッシュだったり、ロジックの問題だったり様々だが、CLIの出力だけでは判断できない。

## 方針: テストコードでUI操作を再現する

### なぜテストコードか

| 手段 | 端末占有 | 再現性 | 自動化 | CIで回せる |
|------|---------|--------|--------|-----------|
| 手動で触る | - | 低い | 不可 | 不可 |
| adb-pilot | する（tap等） | 中 | 可能 | 不可 |
| テストコード | **しない** | **高い** | **可能** | **可能** |

### 使うもの

- **Vitest** — テストランナー（Jest互換、Viteネイティブ）
- **React Testing Library** — ユーザー視点でコンポーネントをテスト
- **@testing-library/user-event** — クリック・入力等のユーザー操作シミュレーション

### 基本パターン

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, test, expect } from 'vitest';

describe('ScheduleScreen', () => {
  test('編集ボタンを押すと編集画面に遷移する', async () => {
    render(<App />);
    
    // ユーザーが「編集」ボタンを押す操作を再現
    await userEvent.click(screen.getByText('編集'));
    
    // 遷移先の画面が表示されていることを確認
    expect(screen.getByText('スケジュール編集')).toBeInTheDocument();
  });

  test('入力欄に名前を入れて保存できる', async () => {
    render(<ScheduleEditScreen />);
    
    await userEvent.type(screen.getByLabelText('名前'), 'テストスケジュール');
    await userEvent.click(screen.getByText('保存'));
    
    expect(screen.getByText('保存しました')).toBeInTheDocument();
  });
});
```

### 実行

```bash
# 全テスト実行
npm test

# 特定ファイルだけ
npx vitest run src/screens/ScheduleScreen.test.tsx

# watchモード（ファイル変更で自動再実行）
npx vitest src/screens/ScheduleScreen.test.tsx
```

## 見た目の検証: Puppeteerで実ブラウザDOM/CSSテスト

jsdomにはCSSエンジンがないため、`getComputedStyle`が空を返す。見た目に関わるテスト（色、visibility、画像読み込み等）は**実ブラウザが必要**。

### なぜPuppeteerか

- proot内にChromium + Puppeteer環境が既にある（browser_crawler.pyで使用中）
- 新しいインストール不要
- Termux上でも動作確認済み
- 端末を占有しない（headlessで動く）

### できること

| テスト対象 | jsdom (Vitest) | Puppeteer |
|-----------|----------------|-----------|
| クリック・遷移 | OK | OK |
| テキスト表示 | OK | OK |
| CSS計算値（色、サイズ） | **不可** | **OK** |
| display:none / visibility:hidden | 一部 | **OK** |
| 画像の実読み込み | **不可** | **OK** |
| レイアウト（位置、重なり） | **不可** | **OK** |

### 基本パターン

```js
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://localhost:5173/#/schedule');

  // CSS計算済みの色を検証
  const bgColor = await page.$eval('.primary-button', el =>
    getComputedStyle(el).backgroundColor
  );
  console.assert(bgColor === 'rgb(0, 122, 255)', `色が違う: ${bgColor}`);

  // 画像が実際に読み込まれているか
  const imgLoaded = await page.$eval('img.logo', el =>
    el.complete && el.naturalWidth > 0
  );
  console.assert(imgLoaded, '画像が読み込まれていない');

  // 要素が実際に見えているか（CSS計算結果で判定）
  const visible = await page.$eval('.modal', el => {
    const s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0';
  });
  console.assert(visible, 'モーダルが見えていない');

  // スクショで目視確認もできる
  await page.screenshot({ path: '/tmp/test-schedule.png' });

  await browser.close();
})();
```

### 実行（proot経由）

```bash
proot-distro login ubuntu -- node test-visual.js
```

### browser_crawler.pyの仕組みを転用する場合

browser-save.jsのサーバーモードを使えば、ブラウザ起動を1回で済ませて複数ページをテストできる：

```bash
# サーバー起動（1回）
proot-distro login ubuntu -- node bin/browser-save.js --server 3100

# 各ページをテスト（タブ開閉だけなので高速）
curl -X POST http://127.0.0.1:3100/save \
  -H 'Content-Type: application/json' \
  -d '{"url": "http://localhost:5173/#/schedule", "output": "/tmp/test.html"}'
```

保存されたHTMLにはCSS/画像がインライン化されているので、DOMを解析すれば実装と比較できる。

## 補助: adb-pilotでスクショ確認

Puppeteerテストを組むほどでもない軽い確認には、adb-pilotのスクショ機能を使う。スクショは端末を占有しない。

```bash
python3 ~/work/shimatoshi/research-reports/toolbox/adb-pilot/pilot.py screenshot /tmp/screen.png
```

## まとめ

| 検証対象 | ツール |
|---------|--------|
| ロジック・遷移・表示テキスト | Vitest + React Testing Library |
| CSS・色・画像・レイアウト | Puppeteer（proot内Chromium） |
| サクッと目視確認 | adb-pilotスクショ |
| **CLIの「成功」** | **信用しない** |
