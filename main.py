from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)
hubspot_client = HubSpot(access_token=HUBSPOT_TOKEN)

def generate_sales_email(company_name, industry):
    prompt = f"""あなたは優秀な営業担当者です。以下の企業に向けた営業メールを日本語で作成してください。

企業名：{company_name}
業種：{industry}

以下のルールを厳守してください：
- 件名を1行で書く
- 本文は200〜300文字程度で簡潔にまとめる
- 内容の繰り返しは絶対にしない
- 署名は「[名前][会社名][連絡先]」の1回のみ
- 出力は件名と本文と署名のみ"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 業種を日本語→HubSpotコードに変換
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

def save_to_hubspot(company_name, industry, email_content):
    # 日本語業種をHubSpotコードに変換（該当なければそのまま）
    hubspot_industry = INDUSTRY_MAP.get(industry, "OTHER")

    properties = {
        "name": company_name,
        "industry": hubspot_industry,
        "description": email_content[:1000]
    }
    obj = SimplePublicObjectInputForCreate(properties=properties)
    result = hubspot_client.crm.companies.basic_api.create(
        simple_public_object_input_for_create=obj
    )
    return result.id

# 実行
print("=== AI営業メール自動生成 × HubSpot自動登録システム ===\n")
company = input("企業名を入力してください：")
industry = input("業種を入力してください：")

print("\n 営業メールを生成中...\n")
result = generate_sales_email(company, industry)

print("========== 生成された営業メール ==========\n")
print(result)

print("\n HubSpotに自動登録中...")
company_id = save_to_hubspot(company, industry, result)
print(f" HubSpotに登録完了！（企業ID：{company_id}）")

# ファイルにも保存
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(f"企業名：{company}\n業種：{industry}\n\n{result}")

print(" output.txtにも保存しました")