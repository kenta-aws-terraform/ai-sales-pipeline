from dotenv import load_dotenv
import os
import csv
import json
from groq import Groq
from hubspot import HubSpot
from hubspot.crm.companies import SimplePublicObjectInputForCreate
from hubspot.crm.companies.models import Filter, FilterGroup, PublicObjectSearchRequest

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)
hubspot_client = HubSpot(access_token=HUBSPOT_TOKEN)

INDUSTRY_MAP = {
    "IT": "INFORMATION_TECHNOLOGY_AND_SERVICES",
    "金融": "FINANCIAL_SERVICES",
    "製造": "MACHINERY",
    "不動産": "REAL_ESTATE",
    "医療": "HOSPITAL_HEALTH_CARE",
    "教育": "EDUCATION_MANAGEMENT",
    "小売": "RETAIL",
    "飲食": "RESTAURANTS",
    "建設": "CONSTRUCTION",
    "物流": "LOGISTICS_AND_SUPPLY_CHAIN",
    "広告": "MARKETING_AND_ADVERTISING",
    "コンサル": "MANAGEMENT_CONSULTING",
    "保険": "INSURANCE",
    "通信": "TELECOMMUNICATIONS",
    "エネルギー": "OIL_ENERGY",
}

def load_leads_from_csv(filepath):
    """CSVからリードを読み込む"""
    leads = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    print(f" {len(leads)}社のリードをCSVから読み込みました")
    return leads

def company_exists_in_hubspot(company_name):
    """HubSpotに既に登録済みかチェック"""
    filter_ = Filter(property_name="name", operator="EQ", value=company_name)
    filter_group = FilterGroup(filters=[filter_])
    search_request = PublicObjectSearchRequest(filter_groups=[filter_group])
    result = hubspot_client.crm.companies.search_api.do_search(
        public_object_search_request=search_request
    )
    return result.total > 0

def generate_email_and_score(company_name, industry, employee_count, annual_revenue):
    """AIで営業メール生成とリードスコアリングを同時に実行"""
    prompt = f"""あなたは優秀なGTMエンジニアです。以下の企業情報を分析して、2つのタスクをこなしてください。

企業情報：
- 企業名：{company_name}
- 業種：{industry}
- 従業員数：{employee_count}名
- 年間売上：{annual_revenue}

【タスク1】パーソナライズされた営業メールを作成してください。
- 件名を1行で書く
- 本文は200〜300文字で簡潔に
- 企業名・業種・規模を必ず文中に含める
- 繰り返しなし・署名は1回のみ

【タスク2】このリードのスコアリングを行ってください。
以下の基準で100点満点で採点し、理由も書いてください：
- 従業員数が多いほど高スコア
- 売上規模が大きいほど高スコア
- IT・金融・医療は優先度高

必ず以下のJSON形式のみで返答してください（他の文章は不要）：
{{
  "subject": "件名をここに",
  "email_body": "本文をここに",
  "score": 85,
  "score_reason": "スコアの理由をここに"
}}"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    # JSON部分だけ抽出
    start = raw.find("{")
    end = raw.rfind("}") + 1
    json_str = raw[start:end]
    return json.loads(json_str)

def register_to_hubspot(company_name, industry, score, score_reason, email_subject, email_body):
    """HubSpotに企業を登録"""
    hubspot_industry = INDUSTRY_MAP.get(industry, "OTHER")
    properties = {
        "name": company_name,
        "industry": hubspot_industry,
        "description": f"【AIスコア：{score}点】{score_reason}\n\n【生成メール件名】{email_subject}\n\n{email_body[:500]}"
    }
    obj = SimplePublicObjectInputForCreate(properties=properties)
    result = hubspot_client.crm.companies.basic_api.create(
        simple_public_object_input_for_create=obj
    )
    return result.id

def save_results_to_csv(results, filepath="results.csv"):
    """結果をCSVに出力"""
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "company_name", "industry", "score", "score_reason",
            "email_subject", "email_body", "hubspot_id", "status"
        ])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n results.csvに結果を保存しました")

def run_pipeline():
    print("=" * 50)
    print(" AI営業自動化パイプライン 起動")
    print("=" * 50)

    # Step1: CSVからリード読み込み
    leads = load_leads_from_csv("leads.csv")

    results = []

    for i, lead in enumerate(leads, 1):
        company_name = lead["company_name"]
        industry = lead["industry"]
        employee_count = lead["employee_count"]
        annual_revenue = lead["annual_revenue"]

        print(f"\n[{i}/{len(leads)}] 処理中：{company_name}")

        # Step2: HubSpot重複チェック
        if company_exists_in_hubspot(company_name):
            print(f"  ⏭  スキップ（HubSpotに登録済み）")
            results.append({
                "company_name": company_name,
                "industry": industry,
                "score": "-",
                "score_reason": "登録済みのためスキップ",
                "email_subject": "-",
                "email_body": "-",
                "hubspot_id": "-",
                "status": "skipped"
            })
            continue

        # Step3: AIでメール生成＋スコアリング
        print(f"   AIでメール生成・スコアリング中...")
        ai_result = generate_email_and_score(
            company_name, industry, employee_count, annual_revenue
        )
        score = ai_result["score"]
        score_reason = ai_result["score_reason"]
        email_subject = ai_result["subject"]
        email_body = ai_result["email_body"]

        print(f"   スコア：{score}点 - {score_reason}")
        print(f"   件名：{email_subject}")

        # Step4: HubSpotに登録
        print(f"   HubSpotに登録中...")
        hubspot_id = register_to_hubspot(
            company_name, industry, score, score_reason, email_subject, email_body
        )
        print(f"   登録完了（ID：{hubspot_id}）")

        results.append({
            "company_name": company_name,
            "industry": industry,
            "score": score,
            "score_reason": score_reason,
            "email_subject": email_subject,
            "email_body": email_body,
            "hubspot_id": hubspot_id,
            "status": "success"
        })

    # Step5: 結果をCSVに出力
    save_results_to_csv(results)

    # Step6: サマリー表示
    success = len([r for r in results if r["status"] == "success"])
    skipped = len([r for r in results if r["status"] == "skipped"])
    print(f"\n{'=' * 50}")
    print(f" パイプライン完了！")
    print(f"   新規登録：{success}社 / スキップ：{skipped}社")
    if results:
        scored = [r for r in results if r["score"] != "-"]
        if scored:
            top = max(scored, key=lambda x: int(x["score"]))
            print(f"    最優先リード：{top['company_name']}（{top['score']}点）")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    run_pipeline()