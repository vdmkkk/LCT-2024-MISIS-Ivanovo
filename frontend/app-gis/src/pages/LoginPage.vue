<template>
  <q-page class="flex flex-center">
    <q-card class="q-pa-md" style="width: 400px">
      <q-card-section>
        <div class="text-h6">Войти</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="handleSubmit">
          <q-input
            v-model="username"
            label="Логин"
            color="red-10"
            outlined
            required
          />
          <q-input
            style="margin-top: 15px"
            v-model="password"
            label="Пароль"
            type="password"
            outlined
            required
            color="red-10"
          />
          <q-btn
            type="submit"
            label="Login"
            color="red-10"
            class="q-mt-md"
            @click="handleSubmit"
          />
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import login from 'src/api/handleLogin';
import { useRouter } from 'vue-router';
import { ref } from 'vue';

const username = ref('');
const password = ref('');
const router = useRouter();

const handleSubmit = () => {
  login(username.value, password.value);
  router.push('/');
};
</script>

<style scoped>
.q-page {
  background-color: #f5f5f5;
  height: 100vh;
}
</style>
