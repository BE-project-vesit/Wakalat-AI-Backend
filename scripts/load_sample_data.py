"""
Utility script to load sample case law data into the vector database
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.vector_db import get_vector_db
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Sample case law data for demonstration
SAMPLE_CASES = [
    {
        "case_id": "AIR_2020_SC_1234",
        "case_name": "State of Maharashtra v. Prakash Kumar",
        "citation": "AIR 2020 SC 1234",
        "court": "Supreme Court of India",
        "year": 2020,
        "bench": "3-judge bench",
        "date": "2020-03-15",
        "judges": ["Justice A. Sharma", "Justice B. Patel", "Justice C. Kumar"],
        "summary": "This case deals with breach of contract and the calculation of damages. The court held that damages must be reasonable and foreseeable at the time of contract formation.",
        "headnotes": [
            "Contract law - Breach of contract - Damages must be foreseeable",
            "Parties cannot claim for losses that were not contemplated",
            "Standard of reasonable foreseeability applies"
        ],
        "sections_involved": ["Section 73 Contract Act", "Section 74 Contract Act"],
        "precedents_cited": ["Hadley v. Baxendale", "Fateh Chand v. Balkishan Das"],
        "full_text_url": "https://indiankanoon.org/doc/example1",
        "pdf_url": "https://indiankanoon.org/doc/example1.pdf"
    },
    {
        "case_id": "AIR_2019_SC_5678",
        "case_name": "Ram Gopal v. State of UP",
        "citation": "AIR 2019 SC 5678",
        "court": "Supreme Court of India",
        "year": 2019,
        "bench": "2-judge bench",
        "date": "2019-07-22",
        "judges": ["Justice D. Verma", "Justice E. Singh"],
        "summary": "Criminal law case involving Section 302 IPC (murder). The court examined the standard of proof required for circumstantial evidence and upheld the conviction based on chain of circumstances.",
        "headnotes": [
            "Criminal law - Murder - Circumstantial evidence",
            "Chain of circumstances must be complete",
            "No gap should be left in prosecution case",
            "Circumstances should point to guilt of accused only"
        ],
        "sections_involved": ["Section 302 IPC", "Section 304 IPC", "Section 34 IPC"],
        "precedents_cited": ["Sharad Birdhichand Sarda v. State of Maharashtra"],
        "full_text_url": "https://indiankanoon.org/doc/example2",
        "pdf_url": "https://indiankanoon.org/doc/example2.pdf"
    },
    {
        "case_id": "AIR_2021_SC_9012",
        "case_name": "ABC Corporation v. XYZ Industries",
        "citation": "AIR 2021 SC 9012",
        "court": "Supreme Court of India",
        "year": 2021,
        "bench": "3-judge bench",
        "date": "2021-11-10",
        "judges": ["Justice F. Reddy", "Justice G. Mehta", "Justice H. Khan"],
        "summary": "Commercial dispute regarding specific performance of contract. The court held that specific performance is discretionary and monetary compensation may be adequate in certain cases.",
        "headnotes": [
            "Specific performance - Discretionary relief",
            "Adequacy of monetary compensation to be considered",
            "Undue hardship to defendant",
            "Balance of convenience"
        ],
        "sections_involved": ["Section 10 Specific Relief Act", "Section 20 Specific Relief Act"],
        "precedents_cited": ["K.S. Vidyanadam v. Vairavan"],
        "full_text_url": "https://indiankanoon.org/doc/example3",
        "pdf_url": "https://indiankanoon.org/doc/example3.pdf"
    },
    {
        "case_id": "AIR_2018_SC_3456",
        "case_name": "National Insurance Co. v. Injured Person",
        "citation": "AIR 2018 SC 3456",
        "court": "Supreme Court of India",
        "year": 2018,
        "bench": "2-judge bench",
        "date": "2018-05-18",
        "judges": ["Justice I. Jain", "Justice J. Nair"],
        "summary": "Motor Accident Claims case dealing with calculation of compensation for permanent disability. The court laid down guidelines for assessment of future loss of earnings.",
        "headnotes": [
            "Motor Accident Claims - Compensation",
            "Permanent disability - Loss of earning capacity",
            "Multiplier method for future loss",
            "Just and reasonable compensation"
        ],
        "sections_involved": ["Section 166 Motor Vehicles Act"],
        "precedents_cited": ["Sarla Verma v. DTC"],
        "full_text_url": "https://indiankanoon.org/doc/example4",
        "pdf_url": "https://indiankanoon.org/doc/example4.pdf"
    },
    {
        "case_id": "AIR_2022_SC_7890",
        "case_name": "Environmental NGO v. State",
        "citation": "AIR 2022 SC 7890",
        "court": "Supreme Court of India",
        "year": 2022,
        "bench": "3-judge bench",
        "date": "2022-08-25",
        "judges": ["Justice K. Rao", "Justice L. Gupta", "Justice M. Sinha"],
        "summary": "Environmental law case regarding pollution control. The court applied polluter pays principle and ordered compensation for environmental damage.",
        "headnotes": [
            "Environmental law - Polluter pays principle",
            "Precautionary principle",
            "Sustainable development",
            "Public interest litigation"
        ],
        "sections_involved": ["Article 21 Constitution", "Environment Protection Act"],
        "precedents_cited": ["M.C. Mehta v. Union of India", "Vellore Citizens Welfare Forum v. Union of India"],
        "full_text_url": "https://indiankanoon.org/doc/example5",
        "pdf_url": "https://indiankanoon.org/doc/example5.pdf"
    }
]


def load_sample_data():
    """Load sample case law data into the vector database"""
    try:
        logger.info("Starting to load sample data into vector database...")
        
        # Get vector database instance
        vector_db = get_vector_db()
        
        # Get current stats
        stats = vector_db.get_collection_stats()
        logger.info(f"Current collection stats: {stats}")
        
        # Load each sample case
        success_count = 0
        for case_data in SAMPLE_CASES:
            case_id = case_data.pop('case_id')
            
            # Add case to vector database
            if vector_db.add_case(case_id, case_data):
                success_count += 1
                logger.info(f"Added case: {case_data['case_name']}")
            else:
                logger.error(f"Failed to add case: {case_data['case_name']}")
        
        # Get updated stats
        stats = vector_db.get_collection_stats()
        logger.info(f"Updated collection stats: {stats}")
        logger.info(f"Successfully loaded {success_count}/{len(SAMPLE_CASES)} sample cases")
        
        return success_count
        
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}", exc_info=True)
        return 0


if __name__ == "__main__":
    result = load_sample_data()
    if result > 0:
        print(f"✓ Successfully loaded {result} sample cases into vector database")
    else:
        print("✗ Failed to load sample data")
        sys.exit(1)
