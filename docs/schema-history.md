import FeatureAvailability from '@site/src/components/FeatureAvailability';

# Schema 히스토리

<FeatureAvailability/>

Schema 히스토리는 Dataset이 시간이 지남에 따라 어떻게 변경되는지 이해하는 데 유용한 도구로, 다음과 같은 경우에 대한 통찰력을 제공하고 데이터 실무자에게 이러한 변경이 발생한 시점을 알려줍니다.

- 새로운 필드가 추가됨
- 기존 필드가 제거됨
- 기존 필드의 타입이 변경됨

Schema 히스토리는 DataHub의 [Timeline API](https://docs.datahub.com/docs/dev-guides/timeline/)를 사용하여 스키마 변경 사항을 계산합니다.

## Schema 히스토리 설정, 사전 요구 사항 및 권한

Schema 히스토리는 스키마 변경이 한 번 이상 발생한 모든 Dataset에 대해 DataHub UI에서 볼 수 있습니다. Dataset을 보려면 사용자에게 **View Entity Page** 권한이 있거나 **임의의** DataHub 역할에 할당되어 있어야 합니다.

## Schema 히스토리 사용하기

Dataset의 Schema 탭으로 이동하면 해당 Dataset의 Schema 히스토리를 볼 수 있습니다. Dataset의 버전이 두 개 이상인 경우, 버전 선택기를 사용하여 임의의 버전에서 Dataset이 어떻게 보였는지 확인할 수 있습니다.
다음은 DataHub 공식 데모 환경에서
<a href="https://demo.datahub.com/dataset/urn:li:dataset:(urn:li:dataPlatform:snowflake,long_tail_companions.adoption.pets,PROD)/Schema?is_lineage_mode=false">Snowflake pets dataset</a>을 사용한 예시입니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/schema-history-latest-version.png"/>
</p>

선택기에서 이전 버전을 클릭하면 당시 스키마가 어떻게 보였는지 확인할 수 있습니다. `status` 필드의 용어집 용어 변경, `created_at` 및 `updated_at` 필드의 설명 변경을 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/schema-history-older-version.png"/>
</p>

이 외에도 각 필드의 가장 최근 변경이 언제 이루어졌는지 보여주는 감사(Audit) 뷰를 토글할 수 있습니다.
테이블 오른쪽 상단의 감사 아이콘을 클릭하여 활성화할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/schema-history-audit-activated.png"/>
</p>

일부 필드는 가장 오래된 dataset 버전에서 추가되었고, 일부는 이번 최신 버전에서만 추가되었음을 확인할 수 있습니다. 최신 버전에서 타입이 변경된 필드도 있습니다!

### GraphQL

- [getSchemaBlame](../graphql/queries.md#getSchemaBlame)
- [getSchemaVersionList](../graphql/queries.md#getSchemaVersionList)

## FAQ 및 문제 해결

**Schema 히스토리 기능에 대한 향후 업데이트 계획은 무엇인가요?**

앞으로 다음과 같은 기능을 추가할 계획입니다.

- 시간이 지남에 따라 다양한 스키마 필드에 어떤 변경이 이루어졌는지 볼 수 있는 선형 타임라인 뷰 지원
- Dataset의 두 버전 간 차이를 강조하는 diff 뷰어 추가
