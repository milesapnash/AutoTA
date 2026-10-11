from item_visitor import ItemVisitor


class ExpiryAuditor(ItemVisitor):
    def visit_key(self, key):
        print("Keys do not expire")

    def visit_certificate(self, certificate):
        print(f"{certificate.get_subject()} expires in "
              f"{certificate.get_days_valid()} days")
