export default function Mascot({ size = 64, mood = "happy" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="72" cy="56" rx="15" ry="21" fill="var(--primary-dark)" transform="rotate(24 72 56)" />
      <ellipse cx="50" cy="60" rx="35" ry="30" fill="var(--primary)" />
      <ellipse cx="50" cy="30" rx="23" ry="21" fill="var(--primary)" />
      <circle cx="41" cy="28" r="5.5" fill="white" />
      <circle cx="42" cy="28" r="2.6" fill="#131B34" />
      <path
        d={mood === "happy" ? "M35 38 Q42 45 49 38" : "M35 40 L49 40"}
        stroke="#131B34" strokeWidth="2.6" strokeLinecap="round" fill="none"
      />
      <path d="M50 30 L61 34 L50 38 Z" fill="#F2A93B" />
    </svg>
  );
}