<template>
  <q-page class="q-pa-md">
    <q-btn label="Назад" color="red-10" @click="router.push('/')" />
    <q-card class="q-pa-md" style="max-width: 600px; margin: auto">
      <p style="font-size: 20px">
        <b
          >Данный раздел сайта является демонстративным ввиду нехватки времени.
          Убедительная просьба пользоваться Swagger сервиса Storage</b
        >
      </p>
      <q-card-section>
        <div class="text-h6">Upload Files</div>
      </q-card-section>

      <q-card-section>
        <q-form
          @submit="handleSubmit"
          style="display: flex; flex-direction: column; gap: 14px"
        >
          <p style="font-size: 12px">
            <i
              >Пожалуйста, добавьте токен Яндекс Геокодера в docker-compose. Мы
              используем Геокодер для преобразования Адреса из таблицы ЦТП в
              координаты. Обратите внимание, что бесплатная версия геокодера
              дает доступ к 1000 запросам в день. При привышении лимита
              геокодирования, будут создаваться ЦТП с координатами {0, 0}</i
            >
          </p>
          <q-file
            v-model="files.file1"
            label="11 таблица"
            filled
            square
            outlined
            required
            color="red-10"
          />
          <q-input
            v-model="sheetName"
            label="Название листа в таблице 5"
            required
            filled
            color="red-10"
          />
          <q-file
            v-model="files.file2"
            label="5 таблица"
            filled
            square
            outlined
            required
            color="red-10"
          />
          <q-file
            v-model="files.file3"
            label="7 таблица"
            filled
            square
            outlined
            required
            color="red-10"
          />
          <q-file
            v-model="files.file4"
            label="Агрегированная таблица"
            filled
            square
            outlined
            required
            color="red-10"
          />
          <q-btn
            type="submit"
            label="Upload"
            class="q-mt-md"
            color="red-10"
            @click="handleSubmit"
          />
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import { storage } from 'src/boot/axios';
import Cookies from 'js-cookie';
import { useRouter } from 'vue-router';
const router = useRouter();

const files = ref({
  file1: null,
  file2: null,
  file3: null,
  file4: null,
  file5: null,
});

const token = Cookies.get('_token');
const sheetName = ref('');

const handleSubmit = async () => {
  const formData1 = new FormData();
  formData1.append('file', files.value.file1);

  const formData2 = new FormData();
  formData2.append('file', files.value.file2);

  const formData3 = new FormData();
  formData3.append('file', files.value.file3);

  const formData4 = new FormData();
  formData4.append('file', files.value.file4);

  try {
    // const [response1, response2, response3, response4, response5, response6] =
    //   await Promise.all([
    //     storage.post(`/upload_file/11/${token}`, formData1, {
    //       headers: { 'Content-Type': 'Content-Type: multipart/form-data' },
    //     }),
    //     storage.post(`/upload_file/5/${sheetName.value}/${token}`, formData2, {
    //       headers: { 'Content-Type': 'Content-Type: multipart/form-data' },
    //     }),
    //     storage.post(`/upload_file/7/${token}`, formData3, {
    //       headers: { 'Content-Type': 'Content-Type: multipart/form-data' },
    //     }),
    //     storage.post(`/upload_file/aggregated/${token}`, formData4, {
    //       headers: { 'Content-Type': 'Content-Type: multipart/form-data' },
    //     }),
    //   ]);
    // console.log('File 1 uploaded:', response1.data);
    // console.log('File 2 uploaded:', response2.data);
    // console.log('File 3 uploaded:', response3.data);
    // console.log('File 4 uploaded:', response4.data);
    // console.log('File 5 uploaded:', response5.data);
  } catch (error) {
    console.error('Error uploading files:', error);
  }
};
</script>

<style scoped>
.q-page {
  background-color: #f5f5f5;
  height: 100vh;
}
</style>
