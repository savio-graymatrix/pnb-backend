from pnb.db.data_models.credit_assist.Instruction import *
from pnb.db.data_models.credit_assist.Review import *
from pnb.db.data_models.generic.File import *
from pnb.db.data_models.credit_assist.LoanApplication import *
from pnb.db.data_models.credit_assist.ExtractedDocument import *
from pnb.db.data_models.procurement.Tender import *
from pnb.db.data_models.procurement.Query import *
from pnb.db.data_models.procurement.Bid import *

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
    Bid
]