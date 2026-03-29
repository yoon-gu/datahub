# UI를 통한 데이터 Lineage 관리

## 데이터 Lineage 조회

UI는 데이터 lineage의 최신 버전을 표시합니다. 타임피커를 사용하면 최신 버전 내의 엣지 중 지정된 시간 범위 밖에서 마지막으로 업데이트된 엣지를 필터링하여 제외할 수 있습니다. 과거 시간 범위를 선택해도 과거 데이터 lineage 이력을 보여주지 않습니다. 이 기능은 최신 lineage 버전의 뷰를 필터링하는 용도로만 사용됩니다.

## Lineage 그래프 뷰에서 편집

upstream 또는 downstream lineage를 추가하기 전에 upstream과 downstream entity 모두에 `Edit lineage` 권한이 있는지 확인하세요.

entity의 lineage를 편집할 수 있는 첫 번째 방법은 Lineage 시각화 화면에서입니다. entity 프로필의 오른쪽 상단에 있는 "Lineage" 버튼을 클릭하면 이 화면으로 이동합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/lineage-viz-button.png"/>
</p>

lineage를 편집하려는 entity를 찾은 후, 세 개의 점 메뉴 드롭다운을 클릭하여 upstream 방향으로 편집할지 downstream 방향으로 편집할지 선택합니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/edit-lineage-menu.png"/>
</p>

중앙 노드의 downstream에 있는 entity의 upstream lineage를 편집하거나 중앙 노드의 upstream에 있는 entity의 downstream lineage를 편집하려면, 편집하려는 노드에 포커스를 맞추면 됩니다. 원하는 노드에 포커스를 맞춘 후에는 양방향으로 lineage를 편집할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/focus-to-edit.png"/>
</p>

### Lineage 엣지 추가

"Edit Upstream" 또는 "Edit Downstream"을 클릭하면 선택한 방향으로 선택된 entity의 데이터 lineage를 관리할 수 있는 모달이 열립니다. 새 entity에 lineage 엣지를 추가하려면 제공된 검색창에서 이름으로 검색하여 선택하세요. 추가한 내용에 만족하면 "Save Changes"를 클릭합니다. 변경을 원하지 않으면 언제든지 취소하거나 저장하지 않고 종료할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/add-upstream.png"/>
</p>

### Lineage 엣지 제거

lineage 엣지를 추가하는 데 사용하는 것과 동일한 모달에서 lineage 엣지를 제거할 수 있습니다. 제거하려는 엣지를 찾아 오른쪽의 "X"를 클릭하세요. 추가할 때와 마찬가지로 "Save Changes"를 클릭해야 저장되며, 저장하지 않고 종료하면 변경 사항이 적용되지 않습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/remove-lineage-edge.png"/>
</p>

### 변경 사항 검토

lineage가 수동으로 편집될 때마다 변경한 사람과 변경 시간이 기록됩니다. 엣지를 추가하고 제거하는 모달에서 이 정보를 확인할 수 있습니다. 엣지가 수동으로 추가된 경우 사용자 아바타가 해당 엣지와 함께 표시됩니다. 이 아바타에 마우스를 올리면 누가 언제 추가했는지 확인할 수 있습니다.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/lineage-edge-audit-stamp.png"/>
</p>

## Lineage 탭에서 편집

entity의 lineage를 편집할 수 있는 또 다른 방법은 entity 프로필의 Lineage 탭에서입니다. entity 프로필의 "Lineage" 탭을 클릭한 다음, 해당 entity의 upstream 또는 downstream lineage를 편집할 수 있는 "Edit" 드롭다운을 찾으세요.

<p align="center">
  <img width="70%"  src="https://raw.githubusercontent.com/datahub-project/static-assets/main/imgs/lineage/edit-from-lineage-tab.png"/>
</p>

이 뷰에서 모달을 사용하는 방법은 위에서 설명한 Lineage 시각화 화면에서 편집하는 방법과 동일하게 작동합니다.
