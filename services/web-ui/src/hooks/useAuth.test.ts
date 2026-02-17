import { renderHook } from "@testing-library/react";
import { useAuth } from "./useAuth";

it("loads auth from localStorage", () => {
  localStorage.setItem("code-dojo-token", "abc");
  localStorage.setItem("code-dojo-username", "demo");

  const { result } = renderHook(() => useAuth());

  expect(result.current.token).toBe("abc");
  expect(result.current.username).toBe("demo");
  expect(result.current.isAuthenticated).toBe(true);
});
