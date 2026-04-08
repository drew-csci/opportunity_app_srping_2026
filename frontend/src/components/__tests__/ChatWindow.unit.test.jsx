import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ChatWindow from "../ChatWindow";

describe("ChatWindow (unit)", () => {
  it("sends a new message when clicking send", async () => {
    const user = userEvent.setup();
    const onSendMessage = vi.fn();

    render(<ChatWindow organization="Red Cross" messages={[]} onSendMessage={onSendMessage} />);

    await user.type(screen.getByLabelText("message-input"), "What are your hours?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(onSendMessage).toHaveBeenCalledWith("What are your hours?");
  });
});

