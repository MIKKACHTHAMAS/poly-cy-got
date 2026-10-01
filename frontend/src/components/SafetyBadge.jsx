export default function SafetyBadge({
  safe,
  risk,
}) {

  return (
    <div className="safety-badge">

      <strong>
        {safe ? "Safe" : "Safety warning"}
      </strong>

      <span>
        Risk: {risk}
      </span>

    </div>
  );
}