export default function Mascot({ size = 64, mood = "happy" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="50" cy="65" rx="33" ry="25" fill="var(--primary)" />
      <ellipse cx="21" cy="64" rx="7.5" ry="12" fill="var(--primary-dark)" transform="rotate(-18 21 64)" />
      <ellipse cx="79" cy="64" rx="7.5" ry="12" fill="var(--primary-dark)" transform="rotate(18 79 64)" />
      <circle cx="50" cy="36" r="23" fill="var(--primary)" />

      <circle cx="39" cy="35" r="7" fill="white" />
      <circle cx="61" cy="35" r="7" fill="white" />
      <circle cx="40" cy="36" r="3" fill="#2B3A55" />
      <circle cx="62" cy="36" r="3" fill="#2B3A55" />
      <circle cx="41.3" cy="34.3" r="1.1" fill="white" />
      <circle cx="63.3" cy="34.3" r="1.1" fill="white" />

      <ellipse cx="30" cy="44" rx="5" ry="3" fill="#FFB8C6" opacity="0.6" />
      <ellipse cx="70" cy="44" rx="5" ry="3" fill="#FFB8C6" opacity="0.6" />

      <path
        d={mood === "happy" ? "M40 46 Q50 54 60 46" : "M41 48 L59 48"}
        stroke="#2B3A55" strokeWidth="2.6" strokeLinecap="round" fill="none"
      />
      <path d="M47 39 L39 43 L47 47 Z" fill="#F2A93B" />

      <path d="M50 14 L74 22 L50 30 L26 22 Z" fill="var(--primary-dark)" />
      <rect x="47.5" y="29" width="5" height="9" fill="var(--primary-dark)" />
      <circle cx="50" cy="39" r="2.3" fill="#F2A93B" />
    </svg>
  );
}