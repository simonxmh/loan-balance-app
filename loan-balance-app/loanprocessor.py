import csv

class LoanProcessor:

  def __init__(self,models):
    self.facilities=models['facilities']
    self.banks=models['banks']
    self.covenants=models['covenants']
    self._preprocess_convenants()
    self._preprocess_facilities()

    self.distribution_list={}
    self.facility_expected_yields={}
  
  def _preprocess_facilities(self):
    # facilities sorted on cheapest to most expensive in terms of interest, first valid facility will be chosen
    self.facilities=sorted(self.facilities,key=lambda x: x["interest_rate"]) 

  def _preprocess_convenants(self):
    """[summary]
    When there are covenants with empty facility id, we would simply adjust the covenant to apply to all the facilities under the bank
    """    
    adjust_covenants=[]
    for covenant in self.covenants:
      if covenant["facility_id"] == '':
        covenant_bank_id = covenant["bank_id"]
        # add a new covenant for each facility in the bank
        for facility in self.facilities:
          if facility["bank_id"] == covenant_bank_id:
            new_covenant={
              "facility_id": facility["id"],
              "max_default_likelihood": covenant["max_default_likelihood"],
              "bank_id":covenant["bank_id"],
              "banned_state" :covenant["banned_state"],
            }
            adjust_covenants.append(new_covenant)

      else:
        adjust_covenants.append(covenant)
    self.covenants=adjust_covenants
        
   
  def process(self,loan):
    """[summary]
    Args:
        loan (dict): dictionary of the loan object (interest_rate,amount,id,default_likelihood,state)
    """    
    for facility in self.facilities:

      if self._qualify(loan, facility):
        self.distribution_list[loan["id"]] = facility["id"]

        facility["amount"] = str(float(facility["amount"]) - float(loan["amount"]))

        loan_expected_yield = self._compute_yield(loan,facility)
        if facility["id"] not in self.facility_expected_yields:
          self.facility_expected_yields[facility["id"]]=0
        self.facility_expected_yields[facility["id"]] = self.facility_expected_yields[facility["id"]] + loan_expected_yield

        return 
        
  def _qualify(self,loan,facility):
    """[summary]

    Args:
        loan (dict): dictionary of the loan object (interest_rate,amount,id,default_likelihood,state)
        facility_bank_id (int): bank id of the facility to be verified
        facility_id (int): id of facility to be verified
        facility_amount (float): the max amount of loan the facility can hand out
    Returns:
        bool: returns that the loan qualifies that this facility
    """
    facility_id = facility["id"]
    facility_bank_id = facility["bank_id"]
    facility_amount = facility["amount"]

    # facility contains less money than available for the loan
    if float(facility_amount) < float(loan["amount"]):
      return False
    for covenant in self.covenants:
      if facility_bank_id == covenant["bank_id"]:
        
        # facility id exists, so covenant applies only to facility
        if covenant["facility_id"] != '':
          if facility_id == covenant["facility_id"]:
            # if default likelihood greater than acceptible
            if covenant["max_default_likelihood"] != '' and loan["default_likelihood"] > covenant["max_default_likelihood"]:
              return False

            # if state is banned
            if covenant["banned_state"] and loan["state"] == covenant["banned_state"]:
              return False

    return True

  def _compute_yield(self,loan,facility):
    """[summary]

    Args:
        loan (dict): dictionary of the loan object (interest_rate,amount,id,default_likelihood,state)
        facility (dict):  dictionary of the facility object
    Returns:
        int: expected yield from this loan
    """    
    loan_default_likelihood=float(loan["default_likelihood"])
    loan_interest_rate=float(loan["interest_rate"])
    loan_amount=float(loan["amount"])
    facility_interest_rate=float(facility["interest_rate"])
    # use the expected_yield heuristic
    return int(((1.0-loan_default_likelihood) * loan_interest_rate * loan_amount) - (loan_default_likelihood * loan_amount) - (facility_interest_rate * loan_amount))


  def output_assignments(self,filepath):
    """[summary]

    Args:
        filepath (str): write to this path
    """    
    with open(filepath,'w',encoding='utf8',newline='') as outfile:
      fieldnames=["loan_id","facility_id"]
      dw = csv.DictWriter(
        outfile,
        fieldnames=fieldnames,
      )
      dw.writeheader()
      data = [dict(zip(fieldnames, [k, v])) for k, v in self.distribution_list.items()]
      dw.writerows(data)

  def output_yields(self,filepath):
    """[summary]

    Args:
        filepath (str): write to this path
    """    
    with open(filepath,'w',encoding='utf8',newline='') as outfile:
      fieldnames=["facility_id","expected_yield"]
      dw = csv.DictWriter(
        outfile,
        fieldnames=fieldnames,
      )
      dw.writeheader()
      data = [dict(zip(fieldnames, [k, v])) for k, v in self.facility_expected_yields.items()]
      dw.writerows(data)
