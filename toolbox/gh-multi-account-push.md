# gh CLIで複数アカウントを切り替えずにpushする

`gh auth login` で複数アカウントを登録しているとき、`gh auth switch` でactiveを切り替えなくても、対象アカウントのトークンをURLに直接埋め込めば任意のアカウントとしてpushできる。

## 前提

複数アカウントが `gh auth status` に並んでいる状態。

```bash
$ gh auth status
github.com
  ✓ Logged in to github.com account A-account (keyring)
  - Active account: true
  ✓ Logged in to github.com account B-account (keyring)
  - Active account: false
```

この状態で、activeはA-accountのまま B-accountとしてpushしたい。

## 手順

`gh auth token -u <user>` で対象アカウントのトークンを取り出し、push URLに埋める。

```bash
git push "https://x-access-token:$(gh auth token -u B-account)@github.com/OWNER/REPO.git" BRANCH
```

- `x-access-token` の部分はユーザー名相当だが、GitHubのトークン認証ではここは何でもよい（慣習的に `x-access-token`）
- パスワード相当の位置に `gh auth token -u <user>` で取得したトークンを置く
- これでactive切り替え無しに、そのアカウントの権限で認証が通る

## 使いどころ

- 個人アカウントと組織/共有アカウントで同じマシンを使い分けるとき
- 普段は個人アカウントがactiveだが、特定リポジトリだけは別アカウントでpushしたいとき
- `gh auth switch` を挟むとactiveが移ってしまうので、他の作業に影響を出したくないとき

## 注意点

- URLにトークンが入るので、シェル履歴・プロセス一覧・ログに残る可能性がある。共有マシンでは使わない
- `git remote set-url` でこのURLをremoteに保存するとトークンが `.git/config` に平文で残る。**保存しない**こと
- 一回限りの `git push <URL>` 形式に留めるのが安全

## 常用するなら credential helper を分ける

毎回URLを書くのが面倒なら、push時だけ credential helper を切り替える方法もある。

```bash
git -c credential.helper="" \
    -c credential.helper="!f() { echo username=B-account; echo password=$(gh auth token -u B-account); }; f" \
    push origin BRANCH
```

エイリアスにしておけば `git push-as-b origin main` で済む。
