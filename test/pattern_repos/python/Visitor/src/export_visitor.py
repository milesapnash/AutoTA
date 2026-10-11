from item_visitor import ItemVisitor


class ExportVisitor(ItemVisitor):
    def visit_key(self, key):
        print(f"Exporting key {key.get_material()}")

    def visit_certificate(self, certificate):
        print(f"Exporting certificate for {certificate.get_subject()}")
