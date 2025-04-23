const messages = [
  "Пойдем гулять в парк?",
  "Кажется, дождь собирается. Лучше пойдем в кино!",
  "Давай, сегодня как раз вышел новый фильм.",
  "Встречаемся через час у кинотеатра.",
];

const search_text = "кино";

const found_message = messages.filter((message) =>
  message.toLowerCase().includes(search_text.toLowerCase()),
);

if (found_message.length > 0) {
  console.log(`Сообщения, содержащие "${search_text}":`);
  found_message.forEach((message) => console.log(`- ${message}`));
} else {
  console.log(`Сообщений, содержащих "${search_text}", не найдено.`);
}
