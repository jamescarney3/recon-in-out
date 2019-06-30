
# import this to take command line args
import sys

# header strings to delimit sections of recon input; make this a tuple
# because this should be immutable and iterable
DELIMITER_HEADERS = ("D0-POS", "D1-TRN", "D1-POS")

# transaction codes associated with cash positive and negative cash position
# changes - need to check for inclusion in immutable enumerable structure
CASH_CODES_IN = ("DEPOSIT", "SELL", "DIVIDEND")
CASH_CODES_OUT = ("FEE", "BUY")

# transaction codes associated with positive and negative share amount changes
# for non-cash account contents - carrying over logic from enums above for
# consistency of abstraction, even though these are just single element tuples
SHARE_CODES_IN = ("BUY")
SHARE_CODES_OUT = ("SELL")


# each line of the both position sections of recon input is a space delimited
# record with shape "{unique symbol} {amount}", so we can iterate over a list of
# records and serialize into a dictionary with k/v pairs {symbol}: {amount};
# this dictionary is the basis for applying transaction data to positions data
# and comparing the results to the next period's positions
def generate_positions_hash(positions):
    return {pos.split(' ')[0]: float(pos.split(' ')[1]) for pos in positions}


# for a given positions hash and transaction record, parse transaction record
# into positional components; update positions hash Cash key value if
# transaction type code matches a string in either cash codes tuple; then if
# transaction record symbol is not "Cash" update position value in hash for that
# symbol key according to transaction type
def process_transaction_record(positions_hash, transaction):
    sym, code, units, cash = transaction.split(' ')
    
    if code in CASH_CODES_IN:
        positions_hash['Cash'] = positions_hash['Cash'] + float(cash)
    elif code in CASH_CODES_OUT:
        positions_hash['Cash'] = positions_hash['Cash'] - float(cash)
    
    if sym != 'Cash':
        if not sym in positions_hash.keys():
            positions_hash[sym] = 0;
            
        if code in SHARE_CODES_IN:
            positions_hash[sym] = positions_hash[sym] + float(units)
        elif code in SHARE_CODES_OUT:
            positions_hash[sym] = positions_hash[sym] - float(units)


# build a dict to capture discrepancies between D0 positions with D1
# transactions applied and D1 positions by subtracting values from processed 
# D0-POS & D1-TRN data hash from associated keys in D1 positions hash
def generate_breaks_hash(statement_positions, ledger_positions):
    breaks = statement_positions.copy() # no need to transform the passed dict
    
    # iterate over D0 positions
    for sym in ledger_positions:
        # add a key to hash copy if non present in order to find difference
        if not sym in breaks.keys():
            breaks[sym] = 0
        breaks[sym] = breaks[sym] - ledger_positions[sym]
    
    # filter out differences of zero since they're not breaks
    breaks_hash = {k:v for k, v in breaks.items() if v != 0}    
    return breaks_hash
    

# read file at path in first command line argument or fall back to included recon.in file
def get_target_input():
    if len(sys.argv) >= 2:
        return sys.argv[1]
    else:
        return "recon.in"
        

# transform break hash k/v pair into recon.out format record string
def format_break_record(sym, amt):
    return ' '.join([sym, str(amt if amt % 1 else int(amt))])


# --- MAIN SCRIPT ---

# open and read target file, split contents by line into record strings
recon_in = open(get_target_input())
records = [rec for rec in recon_in.read().split('\n') if rec != '']
recon_in.close()

# get indices of recon.in section headers
delimiter_idxs = [idx for idx, val in enumerate(records) if val in DELIMITER_HEADERS]

d0_pos = records[delimiter_idxs[0] + 1 : delimiter_idxs[1]]
d1_trn = records[delimiter_idxs[1] + 1 : delimiter_idxs[2]]
d1_pos = records[delimiter_idxs[2] + 1 :]

# build position hashes
ledger_positions = generate_positions_hash(d0_pos)
statement_positions = generate_positions_hash(d1_pos)

# apply transactions to ledger positions hash
for transaction_record in d1_trn:
    process_transaction_record(ledger_positions, transaction_record)

# build breaks hash    
breaking_positions = generate_breaks_hash(statement_positions, ledger_positions)

# transform breaks hash sym/amt pairs into space-delimited record strings
recon_records = [format_break_record(sym, amt) for sym, amt in breaking_positions.items()]

# open a file object to write transformed break record strings
recon_out = open('recon.out', 'w')
recon_out.write('\n'.join(recon_records))
recon_out.close()
