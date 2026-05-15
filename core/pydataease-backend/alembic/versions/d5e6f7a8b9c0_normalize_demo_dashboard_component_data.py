"""normalize demo dashboard component data

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-05-13 00:00:00.000000
"""

from __future__ import annotations

from alembic import op


revision = "d5e6f7a8b9c0"
down_revision = "c4d5e6f7a8b9"
branch_labels = None
depends_on = None


_DEMO_DASHBOARD_ID = 1778561641707434266
_DEMO_COMPONENT_DATA = r'''[
  {
    "x": 1,
    "y": 1,
    "id": "1778561641880424059",
    "name": "用户视图",
    "label": "bar",
    "sizex": 12,
    "sizey": 8,
    "style": {
      "top": 100,
      "left": 100,
      "color": "#000000",
      "width": 600,
      "height": 400,
      "margin": "",
      "rotate": 0,
      "opacity": 1,
      "padding": "",
      "fontSize": 16,
      "fontWeight": 400,
      "borderColor": "#cccccc",
      "borderWidth": 0,
      "borderRadius": 0,
      "letterSpacing": 0
    },
    "events": {},
    "requests": {},
    "component": "UserView",
    "datasetId": "1778561592457469007",
    "miniSizex": 1,
    "miniSizey": 1,
    "propValue": {
      "viewId": "1778561641880424059",
      "fieldId": "",
      "hasEdit": true,
      "textValue": ""
    },
    "trackInfo": "",
    "matrixStyle": {},
    "stylePriority": "view",
    "linkageFilters": [],
    "auxiliaryMatrix": true,
    "commonBackground": {
      "alpha": 100,
      "color": "#ffffff",
      "outerImage": "",
      "borderColor": "#cccccc",
      "borderStyle": "solid",
      "borderWidth": 0,
      "borderRadius": 0,
      "backgroundType": "innerImage",
      "innerImageColor": "#1094E5",
      "backgroundColorSelect": true,
      "backgroundImageEnable": false
    }
  }
]'''


def upgrade() -> None:
    op.execute(
        f"""
        UPDATE data_visualization_info
        SET component_data = '{_DEMO_COMPONENT_DATA}'::jsonb
        WHERE id = {_DEMO_DASHBOARD_ID}
          AND component_data IS NOT NULL
          AND jsonb_typeof(component_data) <> 'array'
        """
    )


def downgrade() -> None:
    op.execute(
        f"""
        UPDATE data_visualization_info
        SET component_data = '{{"_activeViewIds": [1778561641880424059]}}'::jsonb
        WHERE id = {_DEMO_DASHBOARD_ID}
          AND component_data = '{_DEMO_COMPONENT_DATA}'::jsonb
        """
    )
