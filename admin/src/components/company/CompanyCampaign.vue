<template>
  <div>
    <div class="row q-gutter-md">
      <div class="text-h6">{{ t('participation_following') }}</div>
      <q-btn
        v-if="isCompanyAdmin"
        :label="t('report')"
        size="sm"
        color="primary"
        icon="bar_chart"
        @click="onShowStats"
      />
    </div>
    <campaign-charts :item="item" />

    <div class="row q-gutter-md q-mt-xl">
      <div class="text-h6">{{ t('overview') }}</div>
    </div>
    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-md-6">
        <fields-list :items="items1" :dbobject="item" />
      </div>
      <div class="col-12 col-md-6">
        <fields-list :items="items2" :dbobject="item" />
      </div>
    </div>

    <div v-if="hasActions">
      <div class="q-mb-sm">{{ t('company.actions') }}</div>
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-12 col-md-6">
          <div class="text-hint q-mb-sm">{{ t('actions.personnal') }}</div>
          <fields-list :items="actionItems" :dbobject="formattedActions" />
        </div>
        <div class="col-12 col-md-6">
          <div class="text-hint q-mb-sm">{{ t('actions.professional') }}</div>
          <fields-list :items="actionProItems" :dbobject="formattedActions" />
        </div>
      </div>
    </div>

    <div class="row q-gutter-md q-mt-xl">
      <div class="text-h6">
        {{ t('campaign.workplaces.title') }}
        <q-badge color="primary" class="on-right">{{ workplacesCount }}</q-badge>
      </div>
      <q-btn
        v-if="workplacesCount > 0"
        size="sm"
        color="primary"
        :label="t('download_csv')"
        icon="download"
        class="on-right"
        @click="onDownloadWorkplaces"
      />
    </div>
    <div class="q-mt-md">
      <q-icon
        :name="item.open_workplaces ? 'check_box' : 'check_box_outline_blank'"
        size="sm"
        class="q-mr-sm"
      />
      <span class="q-mt-xs">{{ t('campaign.workplaces.open_workplaces') }}</span>
    </div>
    <q-list bordered class="q-mt-md">
      <q-item v-for="(wp, index) in visibleWorkplaces" :key="index" class="workplace">
        <q-item-section>
          <div class="text-overline text-half-muted workplace-name">{{ wp.name }}</div>
          <div class="workplace-address">
            <div>{{ wp.address }}</div>
            <div class="q-mt-sm">
              <a
                :href="`https://www.google.com/maps/search/?api=1&query=${wp.lat},${wp.lon}`"
                target="_blank"
                rel="noopener noreferrer"
              >
                <q-icon name="location_on" class="q-mr-xs" />
                <span>{{ formatCoordinates(wp.lat, wp.lon) }}</span>
              </a>
            </div>
          </div>
        </q-item-section>
        <q-item-section side>
          <div>
            <q-expansion-item
              :label="t('campaign.workplaces.show_isochrone')"
              icon="map"
              expand-icon="expand_more"
              header-class="bg-super-muted"
            >
              <isochrones-map
                :mapId="`map-workplace-${index}`"
                :center="[wp.lon, wp.lat]"
                :reco="wp.address"
                height="400px"
                class="q-pt-md"
              />
              <div class="text-body2 q-mt-sm">
                {{ t('campaign.workplaces.isochrones_hint') }}
              </div>
            </q-expansion-item>
          </div>
        </q-item-section>
      </q-item>
    </q-list>
    <div class="row q-mt-sm">
      <q-btn
        v-if="hasMoreWorkplaces"
        flat
        no-caps
        size="sm"
        color="primary"
        :label="t('show_more')"
        icon="expand_more"
        @click="shownWorkplaces = workplacesCount"
      />
      <q-btn
        v-else-if="shownWorkplaces > SHOW_WORKPLACES_MIN"
        flat
        no-caps
        size="sm"
        color="primary"
        :label="t('show_less')"
        icon="expand_less"
        @click="shownWorkplaces = SHOW_WORKPLACES_MIN"
      />
    </div>

    <div class="row q-gutter-md q-mt-lg">
      <div class="text-h6">
        {{ t('campaign.rewards.title') }}
        <q-spinner-dots v-if="loadingRewards" color="primary" class="on-right" size="sm" />
        <q-badge
          v-if="!loadingRewards && rewardDocs && rewardDocs?.total > 0"
          color="primary"
          class="on-right"
          ><span v-if="assignedRewards !== null">{{ filteredRewards.length }}/</span
          >{{ rewardDocs.total }}</q-badge
        >
      </div>
    </div>
    <div class="q-mb-md">
      {{ t('campaign.rewards.description') }}
    </div>
    <div class="q-mt-md">
      <q-icon
        :name="withRewards ? 'check_box' : 'check_box_outline_blank'"
        size="sm"
        class="q-mr-sm"
      />
      <span class="q-mt-xs">{{ t('campaign.rewards.toggle') }}</span>
    </div>
    <div v-if="withRewards && rewardDocs?.total === 0" class="q-mt-md">
      <div>
        <q-btn
          v-if="isCompanyAdmin"
          size="sm"
          color="secondary"
          icon="upload"
          :label="t('upload')"
          @click="showRewardsUploadDialog = true"
        />
      </div>
      <div class="text-hint q-mt-md">
        {{ t('campaign.rewards.no_rewards') }}
      </div>
    </div>
    <div v-else-if="withRewards && rewardDocs && rewardDocs.total > 0" class="q-mt-md">
      <q-toolbar class="q-pa-none">
        <q-btn
          v-if="isCompanyAdmin"
          size="sm"
          color="secondary"
          icon="upload"
          :label="t('upload')"
          @click="showRewardsUploadDialog = true"
          :disabled="processingRewardId === -1"
        />
        <q-btn
          v-if="isCompanyAdmin"
          size="sm"
          color="primary"
          icon="delete"
          :label="t('delete_all')"
          @click="onRewardsDeleteAll"
          class="on-right"
          :disabled="processingRewardId === -1"
        />
        <q-toggle
          v-model="assignedRewards"
          :label="t('campaign.rewards.assigned_rewards')"
          class="on-right"
          toggle-indeterminate
        />
        <q-space />
        <q-input
          v-model="rewardsSearch"
          :placeholder="t('campaign.rewards.search_placeholder')"
          outlined
          dense
          clearable
          class="on-right"
          debounce="300"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </q-toolbar>
      <q-scroll-area visible style="height: 200px">
        <q-list bordered separator class="q-mt-sm">
          <q-item v-for="(doc, index) in filteredRewards || []" :key="index">
            <q-item-section>
              <q-item-label
                >{{ doc.name }}
                <span class="text-hint on-right">{{ formatBytes(doc.size) }}</span>
                <q-badge v-if="doc.token" color="accent" class="on-right">{{ doc.token }}</q-badge>
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <div class="q-gutter-xs">
                <q-btn
                  flat
                  size="sm"
                  icon="download"
                  @click="onDownloadReward(doc)"
                  :loading="processingRewardId === doc.id"
                  :disable="processingRewardId === doc.id"
                />
                <q-btn
                  flat
                  size="sm"
                  icon="delete"
                  color="negative"
                  @click="onRewardsDelete(doc)"
                  :loading="processingRewardId === doc.id"
                  :disable="processingRewardId === doc.id"
                />
              </div>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </div>

    <div class="row q-gutter-md q-mt-lg">
      <div class="text-h6">{{ t('participants') }}</div>
    </div>
    <div class="q-mb-md">
      {{ t('participants_campaign_hint') }}
    </div>
    <div class="q-mb-lg">
      <q-btn
        v-if="item.slug"
        size="sm"
        color="primary"
        icon-right="content_copy"
        :label="t('survey_link')"
        no-caps
        @click="onSurveyLinkCopy"
      />
      <q-btn
        v-if="isCompanyAdmin"
        :label="t('campaign.email_template.buttonText')"
        outline
        size="sm"
        color="field"
        icon="email"
        class="q-ml-md"
        @click="onShowEmailTemplate"
      />
    </div>

    <company-charts-dialog
      v-if="props.company"
      v-model="showChartsDialog"
      :company="company"
      :campaign="item"
    />
    <email-template-dialog v-if="props.item" v-model="showEmailTemplateDialog" :campaign="item" />

    <rewards-upload-dialog
      v-if="props.item"
      v-model="showRewardsUploadDialog"
      :item="item"
      :rewards="rewardDocs"
      @saved="onLoadRewards"
    />
  </div>
</template>

<script setup lang="ts">
import { copyToClipboard } from 'quasar'
import type {
  Campaign,
  Company,
  EmployerActions,
  RewardDocuments,
  RewardDocument,
} from 'src/models'
import CampaignCharts from 'src/components/charts/CampaignCharts.vue'
import CompanyChartsDialog from 'src/components/company/CompanyChartsDialog.vue'
import FieldsList from 'src/components/FieldsList.vue'
import IsochronesMap from 'src/components/IsochronesMap.vue'
import EmailTemplateDialog from 'src/components/EmailTemplateDialog.vue'
import RewardsUploadDialog from 'src/components/company/RewardsUploadDialog.vue'
import type { FieldItem } from 'src/components/FieldsList.vue'
import { formatCoordinates } from 'src/utils/numbers'
import { notifyInfo } from 'src/utils/notify'
import { actionItems, actionProItems } from 'src/utils/options'
import Papa from 'papaparse'
import { makeSurveyLink } from 'src/utils/links'
import { notifyError } from 'src/utils/notify'
import { formatBytes } from 'src/utils/numbers'

const { t, locale } = useI18n()
const authStore = useAuthStore()
const actionsStore = useActions()
const campaignsStore = useCampaigns()
const rewardsStore = useRewards()

interface Props {
  item: Campaign
  company: Company
}
const props = defineProps<Props>()

const SHOW_WORKPLACES_MIN = 5

const showChartsDialog = ref(false)
const showEmailTemplateDialog = ref(false)
const showRewardsUploadDialog = ref(false)
const shownWorkplaces = ref<number>(SHOW_WORKPLACES_MIN)
const rewardDocs = ref<RewardDocuments | null>(null)
const loadingRewards = ref(false)
const processingRewardId = ref<number | null>(null)
const assignedRewards = ref<boolean | null>(null)
const rewardsSearch = ref<string>('')

const isCompanyAdmin = computed(() => {
  if (!props.company) return false
  return authStore.isAdmin || props.company.administrators?.includes(authStore.profile?.email || '')
})

const withRewards = computed(() => {
  return !!props.item.rewards_message || false
})

const filteredRewards = computed(() => {
  if (!rewardDocs.value || !rewardDocs.value.data) return []
  return [...rewardDocs.value.data]
    .filter((doc) => {
      if (assignedRewards.value === null) return true
      return assignedRewards.value ? doc.token : !doc.token
    })
    .filter((doc) => {
      if (!rewardsSearch.value) return true
      const search = rewardsSearch.value.toLowerCase().trim()
      return (
        doc.name.toLowerCase().includes(search) ||
        (doc.token && doc.token.toLowerCase().includes(search))
      )
    })
    .sort((a, b) => (a.name || '').localeCompare(b.name || ''))
})

const visibleWorkplaces = computed(() => {
  let wps = props.item.workplaces ? [...props.item.workplaces] : []
  // sort by name
  wps.sort((a, b) => a.name.localeCompare(b.name))
  wps = wps.slice(0, shownWorkplaces.value)
  return wps
})
const hasMoreWorkplaces = computed(() => {
  return props.item.workplaces ? props.item.workplaces.length > shownWorkplaces.value : false
})
const workplacesCount = computed(() => {
  return props.item.workplaces ? props.item.workplaces.length : 0
})

const hasActions = computed(
  () =>
    Object.keys(props.item.actions || {}).filter((key) =>
      props.item.actions && props.item.actions[key] ? props.item.actions[key].length > 0 : false,
    ).length > 0,
)

const formattedActions = computed(() => {
  const allActions: EmployerActions = {}
  if (props.item.actions) {
    Object.keys(props.item.actions).forEach((group) => {
      allActions[group] =
        props.item.actions && props.item.actions[group]
          ? props.item.actions[group].map((action) => {
              // check action can be parsed as a number
              const actionId = parseInt(action, 10)
              if (!isNaN(actionId)) {
                const labels = actionsStore.items.find((a) => a.id === actionId)?.labels
                if (labels) {
                  return labels[locale.value] || labels.en || action
                }
                return action
              }
              return t(`actions.${action}`)
            })
          : []
    })
  }
  return allActions
})

const items1: FieldItem[] = [
  {
    field: 'name',
  },
  {
    field: 'contact_name',
    label: 'campaign.contact_name',
  },
  {
    field: 'contact_email',
    label: 'campaign.contact_email',
  },
  {
    field: 'info_url',
    label: 'campaign.info_url',
    links: (val) =>
      val.info_url
        ? [
            {
              label: val.info_url,
              to: val.info_url,
              iconRight: 'open_in_new',
            },
          ]
        : [],
  },
  {
    field: 'nb_employees',
    label: 'campaign.nb_employees',
  },
]

const items2: FieldItem[] = [
  {
    field: 'with_travel_pro',
    label: 'campaign.with_travel_pro',
  },
  {
    field: 'start_date',
    label: 'start_date',
    format: (val: Campaign) => val.start_date?.split('T')[0] || '-',
  },
  {
    field: 'end_date',
    label: 'end_date',
    format: (val: Campaign) => val.end_date?.split('T')[0] || '-',
  },
  {
    field: 'slug',
    label: 'campaign.slug',
    links: () => [
      {
        label: `${props.item.slug}`,
        to: makeSurveyLink(props.item.slug!),
        iconRight: 'open_in_new',
      },
    ],
  },
]

onMounted(onLoadRewards)

function onLoadRewards() {
  if (!props.item) return
  loadingRewards.value = true
  rewardDocs.value = null
  campaignsStore
    .getRewards(props.item)
    .then((rewards) => {
      rewardDocs.value = rewards
    })
    .catch(notifyError)
    .finally(() => {
      loadingRewards.value = false
    })
}

function onSurveyLinkCopy() {
  if (!props.item.slug) return
  copyToClipboard(makeSurveyLink(props.item.slug!))
  notifyInfo(t('survey_link_copied'))
}

function onShowStats() {
  showChartsDialog.value = true
}

function onShowEmailTemplate() {
  showEmailTemplateDialog.value = true
}

function onDownloadWorkplaces() {
  if (!props.item.workplaces || props.item.workplaces.length === 0) {
    notifyInfo(t('company.no_workplaces_to_download'))
    return
  }
  // use ; as separator for better compatibility with Excel in some locales
  const csvData = Papa.unparse(
    props.item.workplaces.map((wp) => ({
      name: wp.name,
      address: wp.address,
      lat: wp.lat,
      lon: wp.lon,
    })),
    { delimiter: ';' },
  )
  const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute(
    'download',
    `${props.company.name}_${props.item.name}_workplaces.csv`.replaceAll(' ', '_'),
  )
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function onDownloadReward(doc: RewardDocument) {
  processingRewardId.value = doc.id || null
  rewardsStore
    .downloadReward(doc)
    .catch(notifyError)
    .finally(() => {
      processingRewardId.value = null
    })
}

function onRewardsDelete(doc: RewardDocument) {
  if (!props.item || doc.id === undefined) return
  processingRewardId.value = doc.id
  rewardsStore
    .deleteReward(doc)
    .then(() => {
      onLoadRewards()
    })
    .catch(notifyError)
    .finally(() => {
      processingRewardId.value = null
    })
}

function onRewardsDeleteAll() {
  if (!props.item) return
  processingRewardId.value = -1 // special value to indicate bulk deletion
  rewardsStore
    .deleteRewards(rewardDocs.value?.data || [])
    .then(() => {
      onLoadRewards()
    })
    .catch(notifyError)
    .finally(() => {
      processingRewardId.value = null
    })
}
</script>

<style scoped>
.workplace {
  padding: 1rem 0.5rem;

  display: grid;
  grid-template-areas:
    'workplace-name workplace-address'
    'workplace-isochrone workplace-isochrone';

  gap: 1rem;
}

.workplace-name {
  grid-area: workplace-name;
}

.workplace-address {
  grid-area: workplace-address;
}

.workplace-isochrone {
  grid-area: workplace-isochrone;
}
</style>
