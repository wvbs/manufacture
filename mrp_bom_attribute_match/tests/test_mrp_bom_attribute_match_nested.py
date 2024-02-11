from .common import TestMrpBomAttributeMatchBase


class TestMrpBomAttributeMatchNested(TestMrpBomAttributeMatchBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def setUp(self):
        super().setUp()
        attr1 = self.env["product.attribute"].create(
            {"name": "style", "display_type": "radio", "create_variant": "always"}
        )
        a1vs = self.env["product.attribute.value"].create(
            [
                {"name": "office", "attribute_id": attr1.id},
                {"name": "gaming", "attribute_id": attr1.id},
            ]
        )

        self.top = self.env["product.template"].create(
            {
                "name": "Top-Level",
                "type": "product",
            }
        )
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": attr1.id,
                "product_tmpl_id": self.top.id,
                "value_ids": [(6, 0, a1vs.ids)],
            }
        )

        self.sub = self.env["product.template"].create(
            {
                "name": "Sub-Level",
                "type": "product",
            }
        )
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": attr1.id,
                "product_tmpl_id": self.sub.id,
                "value_ids": [(6, 0, a1vs.ids)],
            }
        )

        subsub = self.env["product.template"].create(
            {
                "name": "Sub Sub 1",
                "type": "product",
            }
        )
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": attr1.id,
                "product_tmpl_id": subsub.id,
                "value_ids": [(6, 0, a1vs.ids)],
            }
        )

        self.bom_sub = self._create_bom(
            self.sub,
            [
                dict(
                    component_template_id=subsub.id,
                    product_qty=1,
                ),
            ],
        )
        self.bom_top = self._create_bom(
            self.top,
            [
                dict(
                    component_template_id=self.sub.id,
                    product_qty=1,
                ),
            ],
        )

    def test_nested(self):
        BomStructureReport = self.env["report.mrp.report_bom_structure"]

        BomStructureReport._get_report_data(self.bom_sub.id)
        BomStructureReport._get_report_data(self.bom_top.id)

    def test_bom_price_compute(self):
        self.top.product_variant_ids[0]._compute_bom_price(self.bom_top)
        self.sub.product_variant_ids[0]._compute_bom_price(self.bom_sub)
