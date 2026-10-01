export default function Message({
  message,
  isUser,
}) {

  return (
    <div
      className={
        isUser
          ? "message user"
          : "message assistant"
      }
    >
      {message}
    </div>
  );
}