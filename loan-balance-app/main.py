import csv
from loanprocessor import LoanProcessor
from typing import List

def load_model(filepath: str):
  with open(filepath, 'r') as file:
    file_reader = csv.DictReader(file)
    # yield next(file_reader)
    return list(file_reader)

def main():
  # Load Models
  filepaths={
    "facilities" : '../small/facilities.csv',
    "banks": '../small/banks.csv',
    "covenants": '../small/covenants.csv'
  }
  models={}
  for model,filepath in filepaths.items():
    models[model] = load_model(filepath)

  loan_processor = LoanProcessor(models)

  # Stream incoming loan requests
  with open('../small/loans.csv', 'r') as file:
    loan_reader = csv.DictReader(file)
    for loan in loan_reader:
      loan_processor.process(loan)
  
  loan_processor.output_assignments('../assignments.csv')
  loan_processor.output_yields('../yields.csv')


if __name__ == "__main__":
  main()