// src/composables/useNavigation.ts
import { useRouter } from 'vue-router';

export function useNavigation() {
  const router = useRouter();

  const navigateTo = (url: string) => {
    window.location.href = url;
  };

  const pushTo = (path: string) => {
    router.push(path);
  };

  return {
    navigateTo,
    pushTo,
  };
}
