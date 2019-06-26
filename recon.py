
import sys

DELIMITER_HEADERS = ["D0-POS", "D1-TRN", "D1-POS"]

CASH_CODES_IN = ["DEPOSIT", "SELL", "DIVIDEND"]
CASH_CODES_OUT = ["FEE", "BUY"]

TN_CODES_IN = ["BUY"]
TN_CODES_OUT = ["SELL"]

def generate_positions_hash(positions):
    return {pos.split(' ')[0]: float(pos.split(' ')[1]) for pos in positions}


def process_transaction_record(positions_hash, transaction):
    sym, code, units, cash = transaction.split(' ')
    
    if code in CASH_CODES_IN:
        positions_hash['Cash'] = positions_hash['Cash'] + float(cash)
    elif code in CASH_CODES_OUT:
        positions_hash['Cash'] = positions_hash['Cash'] - float(cash)
    
    if sym != 'Cash':
        if not sym in positions_hash.keys():
            positions_hash[sym] = 0;
            
        if code in TN_CODES_IN:
            positions_hash[sym] = positions_hash[sym] + float(units)
        elif code in TN_CODES_OUT:
            positions_hash[sym] = positions_hash[sym] - float(units)


def generate_breaks_hash(statement_positions, ledger_positions):
    breaks_hash = statement_positions.copy()
    
    for sym in ledger_positions:
        if not sym in breaks_hash.keys():
            breaks_hash[sym] = 0
        breaks_hash[sym] = breaks_hash[sym] - ledger_positions[sym]
        
    return breaks_hash
    

def get_target_input():
    if len(sys.argv) >= 2:
        return sys.argv[1]
    else:
        return "recon.in"


# main script
recon_in = open(get_target_input())
records = [rec for rec in recon_in.read().split('\n') if rec != '']
recon_in.close()

delimiter_idxs = [idx for idx, val in enumerate(records) if val in DELIMITER_HEADERS]

d0_pos = records[delimiter_idxs[0] + 1 : delimiter_idxs[1]]
d1_trn = records[delimiter_idxs[1] + 1 : delimiter_idxs[2]]
d1_pos = records[delimiter_idxs[2] + 1:]

ledger_positions = generate_positions_hash(d0_pos)
statement_positions = generate_positions_hash(d1_pos)

for transaction_record in d1_trn:
    process_transaction_record(ledger_positions, transaction_record)
    
breaking_positions = generate_breaks_hash(statement_positions, ledger_positions)

recon_records = [' '.join([sym, str(amt if amt % 1 else int(amt))])
                    for sym, amt
                    in breaking_positions.items()
                    if amt != 0]
                    
recon_out = open('recon.out', 'w')
recon_out.write('\n'.join(recon_records))
recon_out.close()
