let bonusBalance = 1000;

const purchace_bonus = 50;
const burn_balance = 3;

let total_purchases = 2; // пусть будет 2 покупки
let total_added = total_purchases * purchace_bonus;
let total_burned = 7 * burn_balance; // в течении 7-ми дней

let final_balance = bonusBalance + total_added - total_burned;

console.log("Баланс через 7 дней: " + final_balance);
