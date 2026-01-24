
function formatDate(date, format = 'YYYY-MM-DD') {
  const d = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(d.getTime())) {
    return '';
  }

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');

  if (format === 'YYYY-MM-DD') {
    return `${year}-${month}-${day}`;
  }

  return `${year}/${month}/${day}`;
}

const data = [
    { date: "2026-01-23" },
    { date: "2025-12-31" },
    { date: "2024-01-01" },
    { date: "1992-04-29" }
];

const testDate = new Date("2025-01-01T00:00:00"); // Local time might vary, but let's assume local
console.log("Test Date:", testDate.toString());
const startDate = formatDate(testDate);
console.log("Formatted Start Date:", startDate);

const filtered = data.filter(item => {
    if (startDate && item.date < startDate) return false;
    return true;
});

console.log("Filtered Data (>= 2025-01-01):", filtered);

const testDate2 = new Date("2026-02-01T00:00:00");
const endDate = formatDate(testDate2);
console.log("Formatted End Date:", endDate);

const filtered2 = data.filter(item => {
    if (endDate && item.date > endDate) return false;
    return true;
});

console.log("Filtered Data (<= 2026-02-01):", filtered2);
