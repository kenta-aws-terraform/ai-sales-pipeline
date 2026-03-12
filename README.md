# AI営業自動化パイプライン × HubSpot連携

## 概要
Groq APIとHubSpot APIを連携させた営業業務の自動化システムです。
リードリストを読み込み、AIによるパーソナライズメール生成・スコアリングを行い、CRMに自動登録します。

## システム構成
```
leads.csv（リストを入力）
　↓
pipeline.py（自動読み込み）
　↓
HubSpot API（重複チェック）
　↓
Groq API / LLaMA-3.3（メール生成・スコアリング）
　↓
HubSpot CRM（自動登録）
　↓
results.csv（結果を自動出力）
```

## 使用技術
- Python 3.x
- Groq API（LLaMA-3.3-70b）
- HubSpot API（CRM連携）
- python-dotenv（環境変数管理）

## 機能一覧
- CSVからリードを自動読み込み
- HubSpotの重複チェック（登録済み企業をスキップ）
- LLMによる企業ごとのパーソナライズ営業メール自動生成
- AIによるリードスコアリング（優先度の自動判定）
- HubSpot CRMへの自動一括登録
- 結果をresults.csvに自動出力

## ファイル構成
```
ai-sales-pipeline/
├── main.py          # プロトタイプ：1社ずつ動作検証
├── pipeline.py      # 本番版：複数社の完全自動化パイプライン
├── reset_demo.py    # デモ用リセットスクリプト
├── leads.csv        # リードリスト（インプット）
├── results.csv      # 処理結果（自動生成）
└── README.md
```

## セットアップ

### 1. リポジトリをクローン
```bash
git clone https://github.com/ユーザー名/ai-sales-pipeline.git
cd ai-sales-pipeline
```

### 2. ライブラリをインストール
```bash
pip install groq hubspot-api-client python-dotenv
```

### 3. 環境変数を設定
`.env`ファイルをプロジェクトルートに作成し、以下を入力：
```
GROQ_API_KEY=your_groq_api_key
HUBSPOT_TOKEN=your_hubspot_token
```

### 4. 実行
```bash
python pipeline.py
```

## 実行結果サンプル
```
 AI営業自動化パイプライン 起動
 5社のリードをCSVから読み込みました
[1/5] 処理中：株式会社テックイノベーション
   AIでメール生成・スコアリング中...
   スコア：80点 - IT業界・従業員150名・売上5億円
   件名：【株式会社テックイノベーション様】IT業界の最新トレンドについて
   登録完了（ID：313602540225）
 パイプライン完了！
   新規登録：5社 / スキップ：0社
    最優先リード：山田フィナンシャル（85点）
```