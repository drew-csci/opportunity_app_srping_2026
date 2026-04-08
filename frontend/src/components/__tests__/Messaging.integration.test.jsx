import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import Messaging from "../Messaging";

describe("Messaging (integration)", () => {
  it("supports full flow: select conversation, send message, and show mock FAQ response", async () => {
    const user = userEvent.setup();

    render(<Messaging />);

    await user.click(screen.getByRole("button", { name: /Food Bank/i }));

    await user.type(screen.getByLabelText("message-input"), "What are your hours?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByText("What are your hours?")).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText("Our volunteer hours are Monday-Friday, 9:00 AM to 5:00 PM.")
      ).toBeInTheDocument();
    });
  });
});

