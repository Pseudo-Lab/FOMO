---
globs: "*.tsx"
description: React Native mobile-specific patterns (supplements typescript.md)
---

# React Native Rules

This supplements the TypeScript rules with mobile-specific patterns.

## Navigation
- Use React Navigation (or Expo Router if Expo project).
- Type all navigation params with a RootStackParamList.
- Handle deep linking configuration early.

## Performance
- Use `FlatList` or `FlashList` for lists, never `ScrollView` with `.map()`.
- Wrap expensive components in `React.memo()`.
- Avoid inline styles in render — use `StyleSheet.create()`.
- Minimize re-renders: check with React DevTools Profiler.

## Platform handling
- Use `Platform.select()` or `Platform.OS` for platform-specific logic.
- Keep platform-specific files as `{Component}.ios.tsx` / `{Component}.android.tsx` only when behavior differs significantly.
- Test on both iOS and Android before shipping.

## Styling
- Use `StyleSheet.create()` for all styles.
- Use responsive units: avoid hardcoded pixel values for spacing.
- Support dark mode from the start with `useColorScheme()`.
- Respect safe areas with `SafeAreaView` or `useSafeAreaInsets()`.

## Storage & state
- Use `AsyncStorage` for simple key-value persistence.
- Use `zustand` or `jotai` for state management (avoid Redux for new projects).
- Never store sensitive data in AsyncStorage — use `expo-secure-store` or platform keychain.

## Error handling
- Wrap the app in an Error Boundary component.
- Handle offline state gracefully — check `NetInfo` before API calls.
- Show user-friendly error messages, not technical errors.

## Testing
- Use React Native Testing Library for component tests.
- Use Detox or Maestro for E2E tests.
- Test on real devices before release, not just simulators.
