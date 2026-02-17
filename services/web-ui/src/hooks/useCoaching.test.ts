import { renderHook } from "@testing-library/react";
import { useCoaching } from "./useCoaching";

it("starts with default state", () => {
  const { result } = renderHook(() => useCoaching());

  expect(result.current.steps).toEqual([]);
  expect(result.current.result).toBeNull();
  expect(result.current.isStreaming).toBe(false);
});
