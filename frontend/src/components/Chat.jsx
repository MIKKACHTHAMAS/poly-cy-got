import { useState } from "react";

import { sendMessage } from "../services/api";

import Message from "./Message";
import SafetyBadge from "./SafetyBadge";


export default function Chat() {

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);


  async function handleSubmit(event) {

    event.preventDefault();

    if (!input.trim()) {
      return;
    }


    const userMessage = input;

    setMessages((previous) => [
      ...previous,
      {
        text: userMessage,
        user: true,
      },
    ]);

    setInput("");
    setLoading(true);


    try {

      const result =
        await sendMessage(userMessage);


      setMessages((previous) => [
        ...previous,
        {
          text: result.response,
          user: false,
          safe: result.safe,
          risk: result.risk,
          reasons: result.reasons,
        },
      ]);

    } catch (error) {

      setMessages((previous) => [
        ...previous,
        {
          text:
            "Unable to contact the server.",
          user: false,
        },
      ]);

    } finally {

      setLoading(false);
    }
  }


  return (
    <div className="chat">

      <div className="messages">

        {messages.map(
          (message, index) => (

            <div key={index}>

              <Message
                message={message.text}
                isUser={message.user}
              />

              {!message.user &&
                message.safe !== undefined && (

                  <SafetyBadge
                    safe={message.safe}
                    risk={message.risk}
                  />

                )}

            </div>

          )
        )}

      </div>


      <form onSubmit={handleSubmit}>

        <input
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          placeholder="Ask PolyCyGot..."
        />

        <button
          type="submit"
          disabled={loading}
        >
          {loading ? "Thinking..." : "Send"}
        </button>

      </form>

    </div>
  );
}