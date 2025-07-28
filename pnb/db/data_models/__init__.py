from pnb.db.data_models.credit_assist.Instruction import *
from pnb.db.data_models.credit_assist.Review import *
from pnb.db.data_models.credit_assist.File import *
from pnb.db.data_models.credit_assist.LoanApplication import *
from pnb.db.data_models.credit_assist.ExtractedDocument import *

DOCUMENT_MODELS = [
    Instruction,
    Review,
    ReviewSet,
    File,
    LoanApplication,
    AgentLifeCycle,
    DocumentChecklist,
    ExtractedDocument

]