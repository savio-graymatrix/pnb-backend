from pnb.db.data_models.credit_assist.Instruction import *
from pnb.db.data_models.credit_assist.Review import *
from pnb.db.data_models.generic.File import *
from pnb.db.data_models.generic.DocumentTemplate import *
from pnb.db.data_models.credit_assist.LoanApplication import *
from pnb.db.data_models.generic.ExtractedDocument import *
from pnb.db.data_models.procurement.Tender import *
from pnb.db.data_models.procurement.Query import *
from pnb.db.data_models.procurement.Bid import *
from pnb.db.data_models.procurement.TenderRule import *
from pnb.db.data_models.call_center.Session import *
from pnb.db.data_models.sales.Product import *
from pnb.db.data_models.sales.Customer import *
from pnb.db.data_models.sales.ProductPurchaseLink import *
from pnb.db.data_models.sales.Lead import *
from pnb.db.data_models.sales.Transaction import *
from pnb.db.data_models.sales.Communication import *


DOCUMENT_MODELS = [
    Instruction,
    Review,
    ReviewSet,
    File,
    LoanApplication,
    AgentLifeCycle,
    DocumentChecklist,
    ExtractedDocument,
    Tender,
    Query,
    Bid,
    TenderRule,
    DocumentTemplate,
    Session,
    CustomerInfo,
    Notes,
    Product,
    Customer,
    ProductPurchaseLink,
    Lead,
    Transaction,
    Communication,
]
