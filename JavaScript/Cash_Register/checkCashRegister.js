function checkCashRegister(price, cash, cid) {
  let owed = cash - price;
  if (owed < 0) {
    owed = price - cash;
  }
  let own = 0;
  let a = { status: "", change: [] };
  let values = [100, 20, 10, 5, 1, 0.25, 0.1, 0.05, 0.01];
  for (let row in cid) {
    own += cid[row][1];
  }
  if (own === owed) {
    a.status = "CLOSED";
    a.change = cid;
    return a;
  }
  if (own < owed) {
    a.status = "INSUFFICIENT_FUNDS";
    a.change = [];
    return a;
  }
  if (own > owed) {
    for (let row in cid.reverse()) {
      let x = cid[row][1] / values[row];
      x = Number(x.toFixed(2));
      if (owed / values[row] > 1) {
        let v = 0;
        while (x > 0 && owed >=values[row]) {
          owed = owed - values[row];
          owed = Number(owed.toFixed(2));
          x--;
          v += values[row];
        };
        v = Number(v.toFixed(2));
        a.change.push([cid[row][0], v]);
      };
    };
    if (owed == NaN || owed == 0) {
      a.status = "OPEN";
      return a;
    } else {
      a.status = "INSUFFICIENT_FUNDS";
      a.change = [];
      return a;
    };
  };
};

checkCashRegister(3.26, 100, [
  ["PENNY", 1.01],
  ["NICKEL", 2.05],
  ["DIME", 3.1],
  ["QUARTER", 4.25],
  ["ONE", 90],
  ["FIVE", 55],
  ["TEN", 20],
  ["TWENTY", 60],
  ["ONE HUNDRED", 100]
]);
