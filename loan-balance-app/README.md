
# How to run

`python3 main.py`

# Write-up

1. How long did you spend working on the problem? What did you find to be the most difficult part?

  Around 3 hours. I found the part where I had to sort out the logic of finding which facilities will not grant the loan due to covenants to be difficult. Especially since there are cases where the covenant can have potentially no facility_id, in which case the covenant would apply to all facilities under the bank. I had to perform a proprocessing of the covenant data to achieve that feature.

2. How would you modify your data model or code to account for an eventual introduction of new, as-of-yet unknown types of covenants, beyond just maximum default likelihood and state restrictions?

  I would remodel the covenant data model to be directly under the facilities. Each facility would present its distinct set of restrictions (some may have been carried down by the orders of the bank). Then when we select from the list of facilities, we can sort it by the cheapest interest rate and then see if the loan qualifies through these restrictions. If we want to add a new type of covenant, the tradeoff for this is we will have to adjust all applicable facilities.

3. How would you architect your solution as a production service wherein new facilities can be introduced at arbitrary points in time. Assume these facilities become available by the finance team emailing your team and describing the addition with a new set of CSVs.

  I would have a method to load the new facility into the data models. All the data I currently load with the object constructor- I would instead use the method to load the facility information, and same goes with all the data model that need restriction. This likely will also have to go through layers of authorization.

4. Your solution most likely simulates the streaming process by directly calling a method in your code to process the loans inside of a for loop. What would a REST API look like for this same service? Stakeholders using the API will need, at a minimum, to be able to request a loan be assigned to a facility, and read the funding status of a loan, as well as query the capacities remaining in facilities.

  POST /loans
  -d {
    interest_rate: <float>
    amount: <int>
    default_likelihood: <float>
    state: <str>
    request_facility_id: <int>
  }
  - GOOD: returns 200, facility id that the loan is assigned to
  - ERR: returns 400, if loan request not fulfillable

  GET /loans/{loans_id}
  - GOOD: returns 200, funding status of the loan
  - ERR: returns 404, loan does not exist

  GET /facilities/{facility_id}
  - GOOD: returns 200, returns funding capacity in facility
  - ERR: returns 404, facility does not exist

  WITH PROPER AUTHZ:

  POST /covenants/
  -d {
    facility_id <int>
    max_default_likelihood <float>
    banned_state: <str>
  }

  POST /facilities/
  -d {
    amount: <int>
    interest_rate: <float>
    bank_id <int>
  }


5. How might you improve your assignment algorithm if you were permitted to assign loans in batch rather than streaming? We are not looking for code here, but pseudo code or description of a revised algorithm appreciated.

If the assignments were done in batch. We can assign loans with knowledge of future loans to use for distributing loans to facilities, in order to optimize the distribution such that resources are optimized.

I would use an dynamic programming algorithm that maximizes the yields. I would use a table to store the yields, with the recurrence formula:


total_yield(l,n) = max( total_yield(l-1,n-1) + calculate_yields[n], # current facility selected for the loan l
                      total_yield(l-1,n-1), # current facility not selected for the loan
)

where n is a qualified facility, and l is loan id

To get the loan assignment, we will need to trace back the dynamic programming steps to see which facilities were selected.

6. Discuss your solution’s runtime complexity.

Time complexity:
Preprocessing done once:
The preprocessing procedure for the covenants is O(c*f) where c = # covenants and f= # facilities. 
The preprocessing procedure for the facilities is O(flogf) for sorting

Loan processing:
For processing the loans, we iterate through all the facilities, and for each facility the covenants to disqualify the facilities. So that process is O(c*f)

Space complexity:

Everything is loaded into memory. The model to process the loans has space O(c+f+b), where c = # covenants, f= # facilities, b= # banks, l=#loans