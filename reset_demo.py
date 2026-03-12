from dotenv import load_dotenv
import os
from hubspot import HubSpot
from hubspot.crm.companies.models import Filter, FilterGroup, PublicObjectSearchRequest

load_dotenv()
hubspot_client = HubSpot(access_token=os.getenv("HUBSPOT_TOKEN"))

DEMO_COMPANIES = [
    "株式会社テックイノベーション",
    "山田フィナンシャル",
    "グリーンエナジー株式会社",
    "株式会社メディカルプラス",
    "東京コンサルティング",
]

def delete_company(company_name):
    filter_ = Filter(property_name="name", operator="EQ", value=company_name)
    filter_group = FilterGroup(filters=[filter_])
    search_request = PublicObjectSearchRequest(filter_groups=[filter_group])
    result = hubspot_client.crm.companies.search_api.do_search(
        public_object_search_request=search_request
    )
    if result.total > 0:
        company_id = result.results[0].id
        hubspot_client.crm.companies.basic_api.archive(company_id=company_id)
        print(f" 削除：{company_name}")
    else:
        print(f" スキップ（未登録）：{company_name}")

print("  デモデータをリセット中...")
for name in DEMO_COMPANIES:
    delete_company(name)
print(" リセット完了！pipeline.pyを実行できます")