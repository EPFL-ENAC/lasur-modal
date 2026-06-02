<template>
  <q-dialog v-model="showDialog" persistent @hide="onHide">
    <q-card class="dialog-md">
      <q-card-actions>
        <div class="text-h6 q-ml-sm">{{ t('campaign.rewards.title') }}</div>
        <q-space />
        <q-btn flat icon="close" color="field" v-close-popup />
      </q-card-actions>
      <q-separator />

      <q-card-section>
        <q-file
          v-model="files"
          clearable
          :label="t('campaign.rewards.upload_files')"
          :hint="t('campaign.rewards.upload_files_hint')"
          outlined
          multiple
          accept=".pdf, .zip"
        />
      </q-card-section>

      <q-separator />

      <q-card-actions align="right">
        <q-btn outline :label="t('cancel')" color="field" :disabled="loading" v-close-popup />
        <q-btn
          :label="t('save')"
          color="primary"
          @click="onSubmit"
          :loading="loading"
          :disabled="loading"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import type { Campaign, RewardDocuments } from 'src/models'
import { notifyError } from 'src/utils/notify'

interface DialogProps {
  modelValue: boolean
  item: Campaign
  rewards?: RewardDocuments | null
}

const props = defineProps<DialogProps>()
const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const campaignsStore = useCampaigns()

const showDialog = ref(props.modelValue)
const loading = ref(false)
const files = ref<Blob[]>([])

watch(
  () => props.modelValue,
  (value) => {
    showDialog.value = value
    if (value) {
      files.value = []
    }
  },
)

function onSubmit() {
  if (!props.item) return
  loading.value = true
  campaignsStore
    .upload_rewards(props.item, files.value)
    .then(() => {
      emit('saved')
      showDialog.value = false
      emit('update:modelValue', false)
    })
    .catch(notifyError)
    .finally(() => {
      loading.value = false
    })
}

function onHide() {
  showDialog.value = false
  emit('update:modelValue', false)
}
</script>
