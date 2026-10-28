const SECTION_META = {
  character: { label: "角色", kicker: "CHARACTER", singular: "角色" },
  clothing: { label: "服装", kicker: "CLOTHING", singular: "服装" },
  pose: { label: "姿势", kicker: "POSE", singular: "姿势" },
  background: { label: "背景", kicker: "BACKGROUND", singular: "背景" },
  expression: { label: "表情", kicker: "EXPRESSION", singular: "表情" },
};
const NATIVE_FACET_LABELS = {
  clothing: { categories: "服装分类", traits: "服装特征" },
  pose: { categories: "姿势分类", traits: "姿势特征" },
  background: { categories: "场景分类", traits: "场景特征" },
  expression: { categories: "表情分类", traits: "表情特征" },
};
const SECTIONS = Object.keys(SECTION_META);
const DRAFT_KEY = "anima-random-studio:draft:v3";
const LEGACY_DRAFT_KEYS = ["anima-random-studio:draft:v2", "anima-random-studio:draft:v1"];
const VIEW_KEY = "anima-random-studio:pool-view:v1";
const THEME_KEY = "anima-random-studio:theme:v1";
const GROUP_TREE_KEY = "anima-random-studio:favorite-tree:v1";
const CUSTOM_GROUP_TREE_KEY = "anima-random-studio:custom-group-tree:v1";
const INTERNAL_HIRES_PERCENT = 45;
const LEGACY_DEFAULT_LORAS = [
  { filename: "anima-highres-aesthetic-boost.safetensors", enabled: true, strength: 0.75 },
  { filename: "BlueArchiveStyleB1.safetensors", enabled: true, strength: 0.95 },
  { filename: "Cunnyfunkyv3.safetensors", enabled: true, strength: 0.75 },
];
const ui = Object.fromEntries(
  [
    "connection",
    "startButton",
    "stopButton",
    "batchState",
    "progressCount",
    "progressFill",
    "batchError",
    "livePreview",
    "sampleProgress",
    "sampleFill",
    "queueBadge",
    "queuePanel",
    "reproduceImage",
    "variantButton",
    "variantCount",
    "replayDrawer",
    "variantDrawer",
    "closeReplayDrawer",
    "closeVariantDrawer",
    "replaySeedSummary",
    "replayStatus",
    "variantStatus",
    "confirmReplay",
    "confirmVariant",
    "variantModes",
    "redrawSections",
    "variantDrawerCount",
    "settingsForm",
    "count",
    "female_count",
    "male_count",
    "peopleTotal",
    "dimensionList",
    "poolOverview",
    "character_detail",
    "manual_artist",
    "manageArtists",
    "artistFavorites",
    "quality_prompt",
    "extra_prompt",
    "negative_prompt",
    "width",
    "height",
    "steps",
    "cfg",
    "cfg_zero_star",
    "second_sampler_enabled",
    "secondSamplerDrawer",
    "second_sampler_steps",
    "second_sampler_cfg",
    "second_sampler_name",
    "second_scheduler",
    "second_sampler_denoise",
    "gallery",
    "emptyState",
    "historyCount",
    "btnSetExportFolder",
    "exportFolderLabel",
    "btnOpenExportFolder",
    "prevPage",
    "nextPage",
    "pageLabel",
    "detailDialog",
    "closeDialog",
    "detailImage",
    "detailPrevious",
    "detailNext",
    "detailNavStatus",
    "imagePreviewDialog",
    "closeImagePreview",
    "imagePreviewPrevious",
    "imagePreviewNext",
    "imagePreviewStage",
    "imagePreviewTitle",
    "imagePreviewImage",
    "imagePreviewVeil",
    "imagePreviewStatus",
    "imagePreviewAnnouncement",
    "detailMeta",
    "detailStats",
    "detailSelection",
    "detailPositive",
    "detailNegative",
    "copyPositivePrompt",
    "copyNegativePrompt",
    "restoreSettings",
    "openFolder",
    "quickExportImage",
    "deleteRecord",
    "toast",
    "poolDrawer",
    "drawerBackdrop",
    "closePool",
    "poolTitle",
    "poolKicker",
    "poolMeta",
    "poolSearch",
    "poolSort",
    "poolLanguage",
    "togglePoolSidebar",
    "selectedOnly",
    "clearFilters",
    "selectPage",
    "selectFiltered",
    "deselectFiltered",
    "selectAllPool",
    "clearPool",
    "favoriteSelection",
    "addCustom",
    "importCustom",
    "poolSidebar",
    "poolGrid",
    "poolEmpty",
    "poseConflict",
    "poolSelectionLabel",
    "poolPrev",
    "poolNext",
    "poolPageLabel",
    "confirmPool",
    "customDialog",
    "customForm",
    "closeCustom",
    "cancelCustom",
    "customDialogTitle",
    "customId",
    "customTitle",
    "customSubtitle",
    "customGenderField",
    "customGender",
    "customCharacterMeta",
    "customHair",
    "customEye",
    "customSeries",
    "customPoseMeta",
    "customCategory",
    "customTraits",
    "customPrompt",
    "customGroupChecks",
    "deleteCustom",
    "loraSummary",
    "loraList",
    "loraEmpty",
    "addLora",
    "resetLoras",
    "loraDialog",
    "closeLora",
    "cancelLora",
    "loraSearch",
    "loraCatalog",
    "loraCatalogEmpty",
    "loraCatalogMeta",
    "loraTriggerDialog",
    "loraTriggerForm",
    "loraTriggerTitle",
    "loraTriggerFilename",
    "loraTriggerWords",
    "loraSourceTriggerWords",
    "closeLoraTriggers",
    "cancelLoraTriggers",
    "resetLoraTriggers",
    "managePromptRules",
    "undoPromptNormalization",
    "promptNormalizationStatus",
    "promptRuleDialog",
    "promptRuleForm",
    "promptRuleList",
    "promptRuleId",
    "promptRuleFrom",
    "promptRuleTo",
    "promptRulePositive",
    "promptRuleNegative",
    "promptRuleLora",
    "promptRuleError",
    "deletePromptRule",
    "clearPromptRule",
    "closePromptRules",
    "cancelPromptRules",
    "draftStatus",
    "resetSettings",
    "clearDraft",
    "favoriteDialog",
    "favoriteForm",
    "favoriteTitle",
    "favoriteGroups",
    "favoriteNickname",
    "removeFavorite",
    "closeFavorite",
    "cancelFavorite",
    "favoriteSelectionDialog",
    "favoriteSelectionForm",
    "favoriteSelectionTitle",
    "favoriteSelectionSummary",
    "favoriteSelectionGroups",
    "favoriteSelectionGroupName",
    "createFavoriteSelectionGroup",
    "favoriteSelectionError",
    "closeFavoriteSelection",
    "cancelFavoriteSelection",
    "confirmFavoriteSelection",
    "groupDialog",
    "groupForm",
    "groupDialogTitle",
    "groupId",
    "groupName",
    "groupNameField",
    "deleteGroup",
    "closeGroup",
    "cancelGroup",
    "saveGroupButton",
    "importChildGroup",
    "childGroupDialog",
    "childGroupForm",
    "childGroupTitle",
    "childGroupHint",
    "childGroupSearch",
    "childGroupList",
    "childGroupEmpty",
    "childGroupError",
    "closeChildGroup",
    "cancelChildGroup",
    "confirmChildGroup",
    "deleteGroupDialog",
    "deleteGroupForm",
    "deleteGroupTitle",
    "deleteGroupSummary",
    "deleteGroupStats",
    "deleteGroupKeep",
    "deleteGroupKeepHint",
    "deleteGroupItemsOption",
    "deleteGroupItems",
    "deleteGroupItemsTitle",
    "deleteGroupItemsHint",
    "deleteGroupAllOption",
    "deleteGroupAll",
    "deleteGroupAllHint",
    "deleteGroupError",
    "closeDeleteGroup",
    "cancelDeleteGroup",
    "confirmDeleteGroup",
    "customGroupDialog",
    "customGroupForm",
    "customGroupDialogTitle",
    "customGroupId",
    "customGroupName",
    "deleteCustomGroup",
    "closeCustomGroup",
    "cancelCustomGroup",
    "importDialog",
    "importDialogTitle",
    "importFile",
    "importBundleName",
    "importJsonTemplate",
    "importCsvTemplate",
    "importTargetGroups",
    "closeImport",
    "cancelImport",
    "importHint",
    "importSummary",
    "importRows",
    "commitImport",
    "artistDialog",
    "closeArtists",
    "cancelArtists",
    "saveCurrentArtists",
    "artistFavoriteList",
    "artistFavoriteCount",
    "newArtistInput",
    "newArtistNickname",
    "btnAddArtist",
    "artistSearchInput",
    "presetSummary",
    "presetError",
    "presetEmpty",
    "presetGrid",
    "presetCollectionsBar",
    "presetSubCollectionsBarWrapper",
    "presetSubCollectionsBar",
    "btnPresetAddSubCollection",
    "presetCollectionsDialog",
    "presetCollectionsForm",
    "presetCollectionsTitle",
    "presetCollectionsSummary",
    "presetCollectionsChecklist",
    "presetCollectionsError",
    "presetDialogParentSelect",
    "presetDialogSubNameInput",
    "btnPresetDialogCreateAndCheck",
    "closePresetCollections",
    "cancelPresetCollections",
    "presetPrevPage",
    "presetNextPage",
    "presetPageLabel",
    "btnTogglePresetBatchMode",
    "btnCreatePreset",
    "tabBtnGallery",
    "tabBtnPresets",
    "galleryCount",
    "presetsCount",
    "galleryViewContainer",
    "presetsViewContainer",
    "presetCreateDialog",
    "presetCreateForm",
    "presetCreateName",
    "presetCreatePreview",
    "presetCreatePlaceholder",
    "presetCreateFile",
    "presetCreateResetCover",
    "presetCreatePickHistory",
    "presetCreateCoverHint",
    "presetCreateError",
    "historyPickerDialog",
    "closeHistoryPicker",
    "cancelHistoryPicker",
    "historyPickerGrid",
    "historyPickerEmpty",
    "historyPickerPrev",
    "historyPickerNext",
    "historyPickerPageLabel",
    "confirmHistoryPicker",
    "closePresetCreate",
    "cancelPresetCreate",
    "presetOverwriteDialog",
    "presetOverwriteForm",
    "presetOverwriteSummary",
    "presetOverwriteThumb",
    "presetOverwriteError",
    "closePresetOverwrite",
    "cancelPresetOverwrite",
    "presetRenameDialog",
    "presetRenameForm",
    "presetRenameName",
    "presetRenameError",
    "closePresetRename",
    "cancelPresetRename",
    "presetDeleteDialog",
    "presetDeleteForm",
    "presetDeleteSummary",
    "presetDeleteError",
    "closePresetDelete",
    "cancelPresetDelete",
    "confirmPresetDelete",
    "recordDeleteDialog",
    "recordDeleteForm",
    "recordDeleteSummary",
    "recordDeleteError",
    "closeRecordDelete",
    "cancelRecordDelete",
    "confirmRecordDelete",
    // 作品库清理(保留最新 N 百张 + 收藏保护)控件
    "btnArchiveCleanup",
    "archiveCleanupDialog",
    "archiveCleanupForm",
    "closeArchiveCleanup",
    "cancelArchiveCleanup",
    "cleanupKeepHundreds",
    "cleanupStatTotal",
    "cleanupStatKeep",
    "cleanupStatProtected",
    "cleanupStatDelete",
    "cleanupStatSize",
    "confirmArchiveCleanup",
    "cleanupError",
    "galleryCollectionsBar",
    "btnGalleryAddCollection",
    "btnPresetAddCollection",
    "commandDeck",
    "btnToggleBatchMode",
    "batchActionBar",
    "batchSelectedCount",
    "batchSelectAll",
    "batchClearSelection",
    "batchExport",
    "batchFavorite",
    "batchDelete",
    "batchExit",
    "detailManageCollections",
    "imageCollectionsDialog",
    "imageCollectionsForm",
    "imageCollectionsChecklist",
    "imageCollectionsError",
    "imageCollectionsBatchWarning",
    "newCollectionNameInput",
    "btnCreateAndCheckCollection",
    "closeImageCollections",
    "cancelImageCollections",
    "saveImageCollections",
    // 新建收藏夹/分类弹窗控件
    "collectionCreateDialog",
    "collectionCreateForm",
    "collectionCreateKicker",
    "collectionCreateTitle",
    "collectionCreateLabel",
    "collectionCreateInput",
    "collectionCreateHint",
    "collectionCreateError",
    "closeCollectionCreate",
    "cancelCollectionCreate",
    "submitCollectionCreate",
    // 重命名收藏夹/分类弹窗控件
    "collectionRenameDialog",
    "collectionRenameForm",
    "collectionRenameKicker",
    "collectionRenameTitle",
    "collectionRenameLabel",
    "collectionRenameInput",
    "collectionRenameHint",
    "collectionRenameError",
    "closeCollectionRename",
    "cancelCollectionRename",
    "submitCollectionRename",
    // 删除收藏夹/分类弹窗控件
    "collectionDeleteDialog",
    "collectionDeleteForm",
    "collectionDeleteKicker",
    "collectionDeleteTitle",
    "collectionDeleteSummary",
    "collectionDeleteHint",
    "collectionDeleteError",
    "closeCollectionDelete",
    "cancelCollectionDelete",
    "confirmCollectionDelete",
    "model_name",
    "sampler_name",
    "scheduler",
    "hires_enabled",
    "hires_model_name",
    "hires_percent",
    "hiresFields",
    "repairSummary",
    "resourceWarning",
    "detailer_hand",
    "detailer_nsfw",
    "detailer_face",
    "detailer_eyes",
    "themeToggle",
    "appError",
  ].map((id) => [id, document.getElementById(id)]),
);

// 0.2.0 新增控件按可选处理:旧版 index.html 缺少它们时只隐藏对应功能,不阻断整个界面。
const OPTIONAL_CONTROLS = new Set([
  "selectFiltered",
  "deselectFiltered",
  "detailPrevious",
  "detailNext",
  "detailNavStatus",
  "livePreview",
  "sampleProgress",
  "sampleFill",
  "queueBadge",
  "queuePanel",
  "reproduceImage",
  "variantButton",
  "variantCount",
  "replayDrawer",
  "variantDrawer",
  "closeReplayDrawer",
  "closeVariantDrawer",
  "replaySeedSummary",
  "replayStatus",
  "variantStatus",
  "confirmReplay",
  "confirmVariant",
  "variantModes",
  "redrawSections",
  "variantDrawerCount",
  // 画师管理弹窗手动录入与检索控件:旧版静态缓存缺少时仅隐藏对应入口,不阻断界面。
  "newArtistInput",
  "newArtistNickname",
  "btnAddArtist",
  "artistSearchInput",
  // 收藏夹常驻新建按钮:旧版 index.html 缺少时仅隐藏新建入口,不阻断界面。
  "btnGalleryAddCollection",
  "btnPresetAddCollection",
  // 预设库子文件夹胶囊栏:旧版 index.html 缺少时仅隐藏二级分类功能,不阻断界面。
  "presetSubCollectionsBarWrapper",
  "presetSubCollectionsBar",
  "btnPresetAddSubCollection",
  // 归类弹窗两级卡片树与快捷新建子文件夹控件:旧版静态缓存缺少时降级为扁平勾选,不阻断界面。
  "presetCollectionsTitle",
  "presetDialogParentSelect",
  "presetDialogSubNameInput",
  "btnPresetDialogCreateAndCheck",
  // 新建/删除收藏夹独立模态弹窗:旧版静态缓存缺少时降级为原生交互,不阻断界面。
  "collectionCreateDialog",
  "collectionCreateForm",
  "collectionCreateKicker",
  "collectionCreateTitle",
  "collectionCreateLabel",
  "collectionCreateInput",
  "collectionCreateHint",
  "collectionCreateError",
  "closeCollectionCreate",
  "cancelCollectionCreate",
  "submitCollectionCreate",
  // 重命名收藏夹/分类弹窗:旧版静态缓存缺少时仅隐藏重命名入口,不阻断界面。
  "collectionRenameDialog",
  "collectionRenameForm",
  "collectionRenameKicker",
  "collectionRenameTitle",
  "collectionRenameLabel",
  "collectionRenameInput",
  "collectionRenameHint",
  "collectionRenameError",
  "closeCollectionRename",
  "cancelCollectionRename",
  "submitCollectionRename",
  "collectionDeleteDialog",
  "collectionDeleteForm",
  "collectionDeleteKicker",
  "collectionDeleteTitle",
  "collectionDeleteSummary",
  "collectionDeleteHint",
  "collectionDeleteError",
  "closeCollectionDelete",
  "cancelCollectionDelete",
  "confirmCollectionDelete",
  // 批量管理控件:旧版 index.html 缺少时整体降级为不可用,不阻断界面。
  "imageCollectionsBatchWarning",
  "commandDeck",
  "btnToggleBatchMode",
  "btnTogglePresetBatchMode",
  "batchActionBar",
  "batchSelectedCount",
  "batchSelectAll",
  "batchClearSelection",
  "batchExport",
  "batchFavorite",
  "batchDelete",
  "batchExit",
  // 作品库清理控件:旧版 index.html 缺少时仅隐藏清理入口,不阻断界面。
  "btnArchiveCleanup",
  "archiveCleanupDialog",
  "archiveCleanupForm",
  "closeArchiveCleanup",
  "cancelArchiveCleanup",
  "cleanupKeepHundreds",
  "cleanupStatTotal",
  "cleanupStatKeep",
  "cleanupStatProtected",
  "cleanupStatDelete",
  "cleanupStatSize",
  "confirmArchiveCleanup",
  "cleanupError",
]);
const missingUi = Object.entries(ui)
  .filter(([id, element]) => !element && !OPTIONAL_CONTROLS.has(id))
  .map(([id]) => id);
if (missingUi.length) {
  const message = `界面资源版本不一致，缺少控件：${missingUi.join("、")}。请刷新页面。`;
  const errorPanel = document.getElementById("appError");
  if (errorPanel) {
    errorPanel.textContent = message;
    errorPanel.hidden = false;
  }
  throw new Error(message);
}

let defaults = null;
let config = { catalog: { counts: {} } };
let currentBatch = null;
let selectedRecord = null;
const imagePreview = {
  phase: "closed", token: 0, zoom: 1, x: 0, y: 0, width: 0, height: 0,
  animation: null, pointers: new Map(), gesture: null, tap: null, backdropPointer: null,
  navigationRequest: 0, preloaded: new Map(), swipe: null,
};
let regenerationOptions = null;
let regenerationRequest = 0;
let regenerationTrigger = null;
let historyPage = 1;
let historyPages = 1;
let historyItems = [];
// 作品库二级筛选:0=全部作品,1=默认收藏,其他为自定义收藏夹 ID。
let activeCollectionId = 0;
let galleryCollections = [];
// 全库图片总数:由 /api/gallery/collections 的 all_total 提供,作为“全部”胶囊的唯一数据源。
let galleryAllTotal = 0;
let galleryCollectionsRequest = 0;
let imageCollectionsSaving = false;
// ---------- 批量管理状态机 ----------
// isBatchMode:是否处于批量选择模式;selectedBatchIds:已选作品 id 集合(跨页保留)。
// lastBatchAnchorId:Shift 区间连选的锚点;batchBusy:批量请求在途时锁定操作条。
let isBatchMode = false;
const selectedBatchIds = new Set();
let lastBatchAnchorId = null;
let batchBusy = false;
let batchBarHideTimer = null;
// 快捷复制目标目录(后端 app_settings.json 持久化,前端仅缓存渲染)
let currentExportFolder = "";
let quickExportInFlight = false;
const historyCache = new Map();
let lastTerminalBatch = "";
let toastTimer = null;
let persistTimer = null;
let initialized = false;
let draft = { modes: {}, counts: {}, fixed: {}, pools: {}, loras: [], managedTriggers: [] };
let activeSection = "character";
let poolPage = 1;
let poolPages = 1;
let poolItems = [];
let poolTotal = 0;
let poolMatchingIds = [];
let poolFacets = {};
let poolRequest = 0;
let editingCustom = null;
let editingCustomGroup = null;
let editingFavoriteItem = null;
let loraInventory = [];
let loraInventoryLoaded = false;
let loraInventoryError = "";
let editingLoraTrigger = null;
let promptRules = [];
let editingPromptRule = null;
let normalizationUndo = null;
let favoritesData = { groups: [], items: [], favorite_keys: [] };
let favoritesAvailable = false;
let customGroups = [];
let artistFavoritesData = { groups: [], items: [] };
let stylePresets = [];
// 预设库纯前端分页状态:每页展示 12 个预设。
let presetPage = 1;
const PRESET_PAGE_SIZE = 12;
// ---------- 预设库批量管理状态机 ----------
// isPresetBatchMode:是否处于预设批量选择模式;selectedPresetBatchIds:跨页保留的预设 ID 集合;
// lastPresetBatchAnchorId:Shift 区间连选锚点;presetBatchBusy:批量请求在途时锁定操作条。
let isPresetBatchMode = false;
const selectedPresetBatchIds = new Set();
let lastPresetBatchAnchorId = null;
let presetBatchBusy = false;
// 预设批量归类弹窗上下文:非空时 #presetCollectionsDialog 进入批量模式。
let presetBatchCollectionsContext = null;
// 预设批量删除弹窗上下文:非空时 #presetDeleteDialog 进入批量模式。
let presetBatchDeleteContext = null;
// ---------- 预设库两级分类状态机 ----------
// currentPresetParentId: 0=全部预设, 1=默认收藏, 其余为自定义母文件夹 ID
let presetCollections = [];
let currentPresetParentId = 0;
// currentPresetSubId: 当前选中的子分类 ID (仅在 parentId > 1 时生效)
let currentPresetSubId = 0;
// 全库预设总数:由 /api/style-presets/collections 的 all_total 提供,作为“全部”胶囊的唯一数据源。
let presetAllTotal = 0;
let presetCollectionsRequest = 0;
// 归类弹窗当前操作的预设对象。
let presetCollectionsTarget = null;
let presetCollectionsSaving = false;
let resources = { models: [], upscale_models: [], samplers: [], schedulers: [] };
let resourceError = "";
let resourcesLoaded = false;
let importPreview = null;
let editingGroup = null;
let childGroupParent = null;
let selectedChildSource = "";
let pendingGroupDelete = null;
let collapsedFavoriteGroups = (() => {
  try {
    const value = JSON.parse(localStorage.getItem(GROUP_TREE_KEY) || "{}");
    return Object.fromEntries(SECTIONS.map((section) => [section, new Set(value[section] || [])]));
  } catch {
    return Object.fromEntries(SECTIONS.map((section) => [section, new Set()]));
  }
})();
const customTreeInitialized = new Set();
let collapsedCustomGroups = (() => {
  try {
    const value = JSON.parse(localStorage.getItem(CUSTOM_GROUP_TREE_KEY) || "{}");
    Object.keys(value).forEach((section) => customTreeInitialized.add(section));
    return Object.fromEntries(SECTIONS.map((section) => [section, new Set(value[section] || [])]));
  } catch {
    return Object.fromEntries(SECTIONS.map((section) => [section, new Set()]));
  }
})();
const poseItemCache = new Map();

function defaultView() {
  return {
    query: "",
    sort: "",
    language: "zh",
    selectedOnly: false,
    blockedOnly: false, // 标识当前是否在查看"隔离屏蔽池"
    scrollTop: 0,
    filters: { gender: "", hair: "", eye: "", series: "", categories: [], traits: [], collection: "", customGroup: "" },
  };
}
let poolViews = Object.fromEntries(SECTIONS.map((section) => [section, defaultView()]));

// 内存屏蔽映射表:各卡池被隔离的预设 ID 集合(与后端 data/blocked_prompts.json 同步)。
let blockedPromptSets = Object.fromEntries(SECTIONS.map((section) => [section, new Set()]));

async function loadBlockedPrompts() {
  try {
    const data = await request("/api/blocked-prompts");
    for (const section of SECTIONS) {
      blockedPromptSets[section] = new Set(data[section] || []);
    }
  } catch (error) {
    console.warn("加载屏蔽池配置失败:", error);
  }
}

async function request(path, options = {}) {
  // FormData 由浏览器自动设置 multipart 边界,不能强制 JSON Content-Type,
  // 否则预设缩略图上传会被服务端按 JSON 解析而失败。
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
  const response = await fetch(path, {
    headers: options.body && !isFormData ? { "Content-Type": "application/json" } : undefined,
    ...options,
  });
  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }
  if (!response.ok) throw new Error(payload.error || `请求失败 (${response.status})`);
  return payload;
}

function escapeHtml(value) {
  const span = document.createElement("span");
  span.textContent = value == null ? "" : String(value);
  return span.innerHTML.replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}

function toast(message) {
  ui.toast.textContent = message;
  ui.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => ui.toast.classList.remove("show"), 3200);
}

// ---------- 快捷复制导出目录:配置同步、胶囊渲染与单图复制 ----------
async function loadExportFolderConfig() {
  try {
    const data = await request("/api/settings/export-folder");
    currentExportFolder = data.export_dir || "";
    renderExportFolderWidget();
  } catch (error) {
    console.error("加载导出目录失败:", error);
  }
}

function renderExportFolderWidget() {
  if (!ui.btnSetExportFolder || !ui.exportFolderLabel) return;
  if (currentExportFolder) {
    const parts = currentExportFolder.replaceAll("\\", "/").split("/").filter(Boolean);
    const folderName = parts.pop() || currentExportFolder;
    ui.exportFolderLabel.textContent = `导出至: ${folderName}`;
    ui.btnSetExportFolder.classList.add("configured");
    ui.btnSetExportFolder.title = `导出目录: ${currentExportFolder} (点击更换)`;
    if (ui.btnOpenExportFolder) ui.btnOpenExportFolder.hidden = false;
  } else {
    ui.exportFolderLabel.textContent = "设置导出目录";
    ui.btnSetExportFolder.classList.remove("configured");
    ui.btnSetExportFolder.title = "点击设置快捷复制的目标文件夹";
    if (ui.btnOpenExportFolder) ui.btnOpenExportFolder.hidden = true;
  }
}

async function triggerPickExportFolder() {
  try {
    toast("请在系统弹窗中选择文件夹...");
    const picked = await request("/api/system/pick-folder", { method: "POST" });
    if (!picked.path) return false;
    const res = await request("/api/settings/export-folder", {
      method: "POST",
      body: JSON.stringify({ export_dir: picked.path }),
    });
    currentExportFolder = res.export_dir || "";
    renderExportFolderWidget();
    toast(`导出目录已设置为: ${currentExportFolder}`);
    return true;
  } catch (error) {
    toast(`设置导出目录失败: ${error.message}`);
    return false;
  }
}

async function executeQuickExport() {
  if (!selectedRecord || quickExportInFlight) return;
  const button = ui.quickExportImage;
  if (!button) return;

  if (!currentExportFolder) {
    toast("请先设置导出目录");
    const ok = await triggerPickExportFolder();
    if (!ok) return;
  }

  const originalText = button.textContent;
  quickExportInFlight = true;
  button.disabled = true;

  try {
    const res = await request(`/api/history/${selectedRecord.id}/copy-to-export`, {
      method: "POST",
    });
    toast(`已复制到 ${res.folder_name}\\${res.filename}`);

    button.classList.add("btn-success");
    button.textContent = "已复制 ✓";
    setTimeout(() => {
      button.classList.remove("btn-success");
      button.textContent = originalText;
      button.disabled = false;
      quickExportInFlight = false;
    }, 1200);
  } catch (error) {
    toast(`复制失败: ${error.message}`);
    button.disabled = false;
    quickExportInFlight = false;
  }
}

async function copyPromptToClipboard(text, button, successMsg) {
  if (!text) {
    toast("内容为空，无需复制");
    return;
  }
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      // 兼容不支持 clipboard API 的后备机制
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }

    toast(successMsg);

    // 图标动画状态切换
    if (button) {
      const iconCopy = button.querySelector(".icon-copy");
      const iconCheck = button.querySelector(".icon-check");
      button.classList.add("copied");
      if (iconCopy && iconCheck) {
        iconCopy.hidden = true;
        iconCheck.hidden = false;
        clearTimeout(button._timer);
        button._timer = setTimeout(() => {
          iconCopy.hidden = false;
          iconCheck.hidden = true;
          button.classList.remove("copied");
        }, 1500);
      }
    }
  } catch (err) {
    toast(`复制失败: ${err.message}`);
  }
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}
const PROMPT_FIELD_NAMES = [
  "quality_prompt",
  "manual_artist",
  "fixed_character",
  "fixed_clothing",
  "fixed_pose",
  "fixed_background",
  "fixed_expression",
  "extra_prompt",
  "negative_prompt",
];
const PROMPT_FIELD_LABELS = {
  quality_prompt: "质量词",
  manual_artist: "画师",
  fixed_character: "固定角色",
  fixed_clothing: "固定服装",
  fixed_pose: "固定姿势",
  fixed_background: "固定背景",
  fixed_expression: "固定表情",
  extra_prompt: "额外提示词",
  negative_prompt: "负面词",
  custom_prompt: "自定义提示词",
};
function promptFieldForElement(element) {
  if (!element) return "";
  if (element.dataset?.fixed) return `fixed_${element.dataset.fixed}`;
  if (element === ui.customPrompt) return "custom_prompt";
  return PROMPT_FIELD_NAMES.includes(element.id) ? element.id : "";
}
function currentPromptFields() {
  return {
    quality_prompt: ui.quality_prompt.value,
    manual_artist: ui.manual_artist.value,
    ...Object.fromEntries(SECTIONS.map((section) => [`fixed_${section}`, draft.fixed[section] || ""])),
    extra_prompt: ui.extra_prompt.value,
    negative_prompt: ui.negative_prompt.value,
  };
}
function applyPromptField(field, value) {
  if (field.startsWith("fixed_")) {
    const section = field.slice(6);
    draft.fixed[section] = value;
    const input = ui.dimensionList.querySelector(`[data-fixed="${section}"]`);
    if (input) {
      input.value = value;
      autoResizeFixedPrompt(input); // 必须补上这句，防止规范化后内容多行但高度卡在单行
    }
    return;
  }
  if (field === "custom_prompt") {
    ui.customPrompt.value = value;
    return;
  }
  if (ui[field]) ui[field].value = value;
}
function setNormalizationUndo(changes) {
  if (!changes.length) return;
  normalizationUndo = Object.fromEntries(changes.map((item) => [item.field, item.before]));
  ui.undoPromptNormalization.hidden = false;
  const labels = changes.map((item) => PROMPT_FIELD_LABELS[item.field] || item.field);
  ui.promptNormalizationStatus.textContent = `已规范 ${changes.length} 个字段：${labels.join("、")}`;
}
function clearNormalizationUndo(message = "编辑结束后自动按 Anima Tag 规范整理。") {
  normalizationUndo = null;
  ui.undoPromptNormalization.hidden = true;
  ui.promptNormalizationStatus.textContent = message;
}
async function normalizePromptFields(fields, { apply = true, recordUndo = true } = {}) {
  const payload = await request("/api/prompts/normalize", {
    method: "POST",
    body: JSON.stringify({ fields, managedTriggers: clone(draft.managedTriggers || []) }),
  });
  if (apply) {
    for (const [field, value] of Object.entries(payload.fields || {})) applyPromptField(field, value);
    if (payload.changed && recordUndo) setNormalizationUndo(payload.changes || []);
    if (payload.changed) schedulePersist();
  }
  return payload;
}
async function normalizePromptElement(element) {
  const field = promptFieldForElement(element);
  if (!field) return;
  try {
    await normalizePromptFields({ [field]: element.value });
  } catch (error) {
    ui.promptNormalizationStatus.textContent = `规范失败：${error.message}`;
    toast(error.message);
  }
}
async function normalizeSettingsPayload(settings) {
  const fields = Object.fromEntries(
    PROMPT_FIELD_NAMES.filter((field) => typeof settings[field] === "string").map((field) => [field, settings[field]]),
  );
  const payload = await request("/api/prompts/normalize", {
    method: "POST",
    body: JSON.stringify({ fields, managedTriggers: settings.lora_managed_triggers || [] }),
  });
  return { ...settings, ...(payload.fields || {}) };
}
function defaultPools() {
  return Object.fromEntries(SECTIONS.map((section) => [section, { mode: "include", ids: [], excluded_ids: [] }]));
}
function currentView() {
  return poolViews[activeSection] || (poolViews[activeSection] = defaultView());
}

function applyTheme(theme, persist = false) {
  const next = theme === "dark" ? "dark" : "light";
  document.documentElement.dataset.theme = next;
  document.querySelector('meta[name="theme-color"]').content = next === "dark" ? "#1c1c1e" : "#f5f5f7";
  ui.themeToggle.title = next === "dark" ? "切换浅色主题" : "切换深色主题";
  ui.themeToggle.setAttribute("aria-label", ui.themeToggle.title);
  ui.themeToggle.setAttribute("aria-pressed", String(next === "dark"));
  ui.themeToggle.querySelector("span").textContent = next === "dark" ? "☀" : "☾";
  if (persist) localStorage.setItem(THEME_KEY, next);
}

function initialTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === "light" || saved === "dark") return saved;
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function normalizeSettings(raw) {
  const merged = { ...defaults, ...raw };
  const hasPools = raw && raw.pools && typeof raw.pools === "object";
  merged.pools = hasPools ? clone(raw.pools) : defaultPools();
  for (const section of SECTIONS) {
    if (!merged.pools[section]) merged.pools[section] = { mode: "include", ids: [], excluded_ids: [] };
    if (!hasPools && raw?.[`random_${section}`]) merged.pools[section].mode = "all";
  }
  const hasLoras = raw && Object.prototype.hasOwnProperty.call(raw, "loras");
  merged.loras = clone(hasLoras ? raw.loras || [] : defaults?.loras || []);
  merged.lora_managed_triggers = normalizeTriggerWords(
    raw?.lora_managed_triggers || defaults?.lora_managed_triggers || [],
  );
  merged.hires = {
    ...(defaults?.hires || { enabled: true, model_name: "", percent: INTERNAL_HIRES_PERCENT }),
    ...(raw?.hires || {}),
  };
  merged.detailers = {
    ...(defaults?.detailers || { hand: false, nsfw: false, face: false, eyes: false }),
    ...(raw?.detailers || {}),
  };
  merged.cfg_zero_star = Boolean(raw?.cfg_zero_star ?? defaults?.cfg_zero_star ?? false);
  merged.second_sampler = {
    ...(defaults?.second_sampler || {
      enabled: false,
      steps: 16,
      cfg: 4,
      sampler_name: defaults?.sampler_name || "",
      scheduler: defaults?.scheduler || "",
      denoise: 0.2,
    }),
    ...(raw?.second_sampler || {}),
  };
  merged.manual_artist = canonicalArtists(merged.manual_artist);
  return merged;
}

/**
 * 健壮的双轨提示词提取函数 (兼容随机池抽卡与原生固定词)
 * @param {Object} image 单张图片的详情对象 (包含 resolved_selection 和 settings)
 * @param {string} section 卡池分类 ('character' | 'clothing' | 'pose' | 'background' | 'expression')
 * @returns {string} 实际生效的提示词文本 (若未使用则返回空字符串)
 */
function getEffectivePromptForSection(image, section) {
  if (!image) return "";

  // 轨 A: 优先检查是否从随机词库池抽中了词条
  const poolItems = (image.resolved_selection && image.resolved_selection[section]) || [];
  if (Array.isArray(poolItems) && poolItems.length > 0) {
    const extracted = poolItems
      .map((item) => (item.prompt || "").trim().replace(/,+$/, ""))
      .filter((p) => p.length > 0)
      .join(", ");
    if (extracted.length > 0) {
      return extracted;
    }
  }

  // 轨 B: 若随机池未抽卡，回退检查生图时原本是否填了固定提示词
  const fixedKey = `fixed_${section}`;
  if (image.settings && typeof image.settings[fixedKey] === "string") {
    const rawFixed = image.settings[fixedKey].trim();
    if (rawFixed.length > 0) {
      return rawFixed;
    }
  }

  // 轨 C: 两个来源都没有词，才确认该板块确实未生效
  return "";
}

/**
 * 载入历史图片设置:在 applySettings 基础上,对 5 大卡池执行双轨提示词回填。
 * 随机池抽卡图片会把实际抽中的词条固化为固定提示词;纯固定词图片保留原词;
 * 仅当两处来源皆为空时才关闭卡池。
 * @param {Object} record 历史记录详情对象 (含 settings 与 resolved_selection)
 */
function applyRecordSettings(record) {
  if (!record || typeof record.settings !== "object") return;

  // 1. 保护工作台当前的运行时状态（生成数量与卡池选择），防止被历史数据冲毁
  const currentCount = Number(ui.count?.value) || 1;
  const currentPools = clone(draft.pools || defaultPools());

  const settings = clone(record.settings || {});
  settings.count = currentCount;
  settings.pools = currentPools; // 拦截历史候选池，保留工作台当前配置

  // 2. 先按常规流程还原模型、采样、人物、LoRA 等全部画面特征参数
  applySettings(settings);

  // 3. 对 5 大卡池执行双轨提取，固化实际使用的提示词并锁定为【固定】模式
  for (const section of SECTIONS) {
    const promptText = getEffectivePromptForSection(record, section);
    if (promptText) {
      draft.fixed[section] = promptText;
      draft.modes[section] = "fixed";
    } else {
      draft.fixed[section] = "";
      draft.modes[section] = "off";
    }
  }

  // 4. 重新渲染工作台维度卡片与概览
  renderDimensions();
  updatePoolOverview();
}

function applySettings(raw) {
  const settings = normalizeSettings(raw || defaults || {});
  for (const [name, value] of Object.entries(settings)) {
    const element = ui[name];
    if (element && !["object", "undefined"].includes(typeof value)) element.value = value;
  }
  ensureSelectValue(ui.model_name, settings.model_name);
  ensureSelectValue(ui.sampler_name, settings.sampler_name);
  ensureSelectValue(ui.scheduler, settings.scheduler);
  ui.cfg_zero_star.checked = Boolean(settings.cfg_zero_star);
  ui.second_sampler_enabled.checked = Boolean(settings.second_sampler.enabled);
  ui.second_sampler_steps.value = Number(settings.second_sampler.steps) || 16;
  ui.second_sampler_cfg.value = Number(settings.second_sampler.cfg) || 4;
  ensureSelectValue(ui.second_sampler_name, settings.second_sampler.sampler_name);
  ensureSelectValue(ui.second_scheduler, settings.second_sampler.scheduler);
  ui.second_sampler_denoise.value = Number.isFinite(Number(settings.second_sampler.denoise))
    ? Number(settings.second_sampler.denoise)
    : 0.2;
  ensureSelectValue(ui.hires_model_name, settings.hires.model_name);
  ui.hires_enabled.checked = Boolean(settings.hires.enabled);
  ui.hires_percent.value = Number(settings.hires.percent) || INTERNAL_HIRES_PERCENT;
  for (const name of ["hand", "nsfw", "face", "eyes"])
    ui[`detailer_${name}`].checked = Boolean(settings.detailers[name]);
  draft = {
    modes: Object.fromEntries(
      SECTIONS.map((section) => [
        section,
        settings[`random_${section}`] ? "pool" : settings[`fixed_${section}`] ? "fixed" : "off",
      ]),
    ),
    counts: Object.fromEntries(SECTIONS.map((section) => [section, Number(settings[`random_${section}_count`] || 1)])),
    fixed: Object.fromEntries(SECTIONS.map((section) => [section, settings[`fixed_${section}`] || ""])),
    pools: clone(settings.pools || defaultPools()),
    loras: clone(settings.loras || []),
    managedTriggers: clone(settings.lora_managed_triggers || []),
  };
  if (loraInventoryLoaded) reconcileLoraTriggers(draft.loras.filter((item) => item.enabled));
  renderDimensions();
  renderLoras();
  renderLoraCatalog();
  updatePeopleTotal();
  updatePoolOverview();
  updateRepairControls();
}

function readSettings() {
  const normalizedArtist = canonicalArtists(ui.manual_artist.value);
  if (ui.manual_artist.value !== normalizedArtist) ui.manual_artist.value = normalizedArtist;
  const settings = {
    count: Number(ui.count.value),
    female_count: Number(ui.female_count.value),
    male_count: Number(ui.male_count.value),
    character_detail: ui.character_detail.value,
    manual_artist: normalizedArtist,
    quality_prompt: ui.quality_prompt.value,
    extra_prompt: ui.extra_prompt.value,
    negative_prompt: ui.negative_prompt.value,
    width: Number(ui.width.value),
    height: Number(ui.height.value),
    steps: Number(ui.steps.value),
    cfg: Number(ui.cfg.value),
    sampler_name: ui.sampler_name.value,
    scheduler: ui.scheduler.value,
    cfg_zero_star: ui.cfg_zero_star.checked,
    second_sampler: {
      enabled: ui.second_sampler_enabled.checked,
      steps: Number(ui.second_sampler_steps.value),
      cfg: Number(ui.second_sampler_cfg.value),
      sampler_name: ui.second_sampler_name.value,
      scheduler: ui.second_scheduler.value,
      denoise: Number(ui.second_sampler_denoise.value),
    },
    pools: clone(draft.pools),
    loras: clone(draft.loras),
    lora_managed_triggers: clone(draft.managedTriggers || []),
    model_name: ui.model_name.value,
    hires: {
      enabled: ui.hires_enabled.checked,
      model_name: ui.hires_model_name.value,
      percent: Number(ui.hires_percent.value) || INTERNAL_HIRES_PERCENT,
    },
    detailers: {
      hand: ui.detailer_hand.checked,
      nsfw: ui.detailer_nsfw.checked,
      face: ui.detailer_face.checked,
      eyes: ui.detailer_eyes.checked,
    },
  };
  for (const section of SECTIONS) {
    settings[`random_${section}`] = draft.modes[section] === "pool";
    settings[`random_${section}_count`] = Number(draft.counts[section] || 1);
    settings[`fixed_${section}`] = draft.modes[section] === "off" ? "" : (draft.fixed[section] || "");
  }
  return settings;
}

function formatSavedTime(timestamp) {
  try {
    return new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(
      new Date(timestamp),
    );
  } catch {
    return "刚刚";
  }
}

function persistNow() {
  if (!initialized) return;
  const savedAt = new Date().toISOString();
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ version: 3, savedAt, settings: readSettings() }));
    for (const key of LEGACY_DRAFT_KEYS) localStorage.removeItem(key);
    localStorage.setItem(VIEW_KEY, JSON.stringify({ version: 1, activeSection, views: poolViews }));
    ui.draftStatus.textContent = `本地草稿已保存 ${formatSavedTime(savedAt)}`;
  } catch {
    ui.draftStatus.textContent = "浏览器未允许保存草稿";
  }
}

function schedulePersist() {
  clearTimeout(persistTimer);
  persistTimer = setTimeout(persistNow, 180);
}

function loadStoredView() {
  try {
    const payload = JSON.parse(localStorage.getItem(VIEW_KEY) || "null");
    if (payload?.version !== 1 || typeof payload.views !== "object") return;
    for (const section of SECTIONS)
      poolViews[section] = {
        ...defaultView(),
        ...(payload.views[section] || {}),
        filters: { ...defaultView().filters, ...(payload.views[section]?.filters || {}) },
      };
    if (SECTIONS.includes(payload.activeSection)) activeSection = payload.activeSection;
  } catch {
    localStorage.removeItem(VIEW_KEY);
  }
}

function loadStoredDraft() {
  try {
    const current = JSON.parse(localStorage.getItem(DRAFT_KEY) || "null");
    const legacy = current
      ? null
      : LEGACY_DRAFT_KEYS.map((key) => JSON.parse(localStorage.getItem(key) || "null")).find(Boolean);
    const payload = current || legacy;
    if (![1, 2, 3].includes(payload?.version) || !payload.settings || typeof payload.settings !== "object") return false;
    const settings = clone(payload.settings);
    if (payload.version === 1 && isLegacyDefaultLoras(settings.loras)) settings.loras = [];
    applySettings(settings);
    if (payload.version !== 3) {
      localStorage.setItem(DRAFT_KEY, JSON.stringify({ version: 3, savedAt: payload.savedAt, settings }));
      for (const key of LEGACY_DRAFT_KEYS) localStorage.removeItem(key);
    }
    ui.draftStatus.textContent = `已恢复草稿 ${formatSavedTime(payload.savedAt)}`;
    return true;
  } catch {
    localStorage.removeItem(DRAFT_KEY);
    for (const key of LEGACY_DRAFT_KEYS) localStorage.removeItem(key);
    return false;
  }
}

function isLegacyDefaultLoras(value) {
  if (!Array.isArray(value) || value.length !== LEGACY_DEFAULT_LORAS.length) return false;
  return value.every((item, index) => {
    const expected = LEGACY_DEFAULT_LORAS[index];
    return (
      normalizedPath(item?.filename) === normalizedPath(expected.filename) &&
      Boolean(item?.enabled) === expected.enabled &&
      Number(item?.strength) === expected.strength
    );
  });
}

function selectedCount(section) {
  const selection = draft.pools[section] || { mode: "include", ids: [], excluded_ids: [] };
  return selection.mode === "all"
    ? Math.max(0, Number(config.catalog?.counts?.[section] || 0) - selection.excluded_ids.length)
    : selection.ids.length;
}

function renderDimensions() {
  ui.dimensionList.replaceChildren(
    ...SECTIONS.map((section) => {
      const meta = SECTION_META[section];
      const mode = draft.modes[section] || "off";
      const count = draft.counts[section] || 1;
      const selected = selectedCount(section);
      const article = document.createElement("article");
      article.className = `dimension-row mode-${mode}`;
      article.dataset.section = section;
      article.innerHTML = `<div class="dimension-heading"><div><span class="dimension-icon">${meta.label.slice(0, 1)}</span><strong>${meta.label}</strong><small>${selected} 项已选</small></div><button class="manage-pool" type="button" data-manage="${section}">管理池 <span aria-hidden="true">→</span></button></div>
      <div class="dimension-mode" role="group" aria-label="${meta.label}模式"><button type="button" data-mode="off" class="${mode === "off" ? "active" : ""}">关闭</button><button type="button" data-mode="pool" class="${mode === "pool" ? "active" : ""}">随机池</button><button type="button" data-mode="fixed" class="${mode === "fixed" ? "active" : ""}">固定</button></div>
      <div class="dimension-body"><label class="draw-count"><span>抽取数量</span><input type="number" min="1" max="${section === "expression" ? 1 : 5}" step="1" value="${section === "expression" ? 1 : count}" data-count="${section}" ${mode !== "pool" || section === "expression" ? "disabled" : ""}></label><span class="mode-note">${mode === "pool" ? `${selected} 项候选` : mode === "fixed" ? "使用固定提示词" : "不加入提示词"}</span></div>
      <label class="field dimension-fixed"><span>固定提示词</span><textarea rows="1" data-fixed="${section}" placeholder="留空则不加入" ${mode !== "fixed" ? "disabled" : ""}>${escapeHtml(draft.fixed[section] || "")}</textarea></label>`;
      article.querySelectorAll("[data-mode]").forEach((button) =>
        button.addEventListener("click", () => {
          draft.modes[section] = button.dataset.mode;
          renderDimensions();
          schedulePersist();
        }),
      );
      article.querySelector("[data-count]").addEventListener("input", (event) => {
        draft.counts[section] = Math.max(1, Math.min(5, Number(event.target.value || 1)));
        schedulePersist();
        updatePoseConflict();
      });
      const fixedInput = article.querySelector("[data-fixed]");
      // 输入时同步草稿并触发高度伸缩
      fixedInput.addEventListener("input", (event) => {
        draft.fixed[section] = event.target.value;
        autoResizeFixedPrompt(fixedInput);
        schedulePersist();
      });
      // 失焦规范化 Anima Tag
      fixedInput.addEventListener("blur", () => normalizePromptElement(fixedInput));
      // 快捷键体验优化：Ctrl+Enter 或 Cmd+Enter 直接触发生成
      fixedInput.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
          event.preventDefault();
          ui.settingsForm.requestSubmit();
        }
      });
      // 挂载前/后执行一次高度自适应，保证历史记录或草稿还原时多行内容立刻撑开
      requestAnimationFrame(() => autoResizeFixedPrompt(fixedInput));
      article.querySelector("[data-manage]").addEventListener("click", () => openPool(section));
      return article;
    }),
  );
}

function updatePeopleTotal() {
  const total = Number(ui.female_count.value || 0) + Number(ui.male_count.value || 0);
  ui.peopleTotal.textContent = total ? `共 ${total} 人` : "不限人数";
}
function updatePoolOverview() {
  ui.poolOverview.textContent = `${SECTIONS.reduce((sum, section) => sum + selectedCount(section), 0)} 项已选`;
}

function normalizedPath(value) {
  return String(value || "")
    .replaceAll("\\", "/")
    .toLowerCase();
}
function updateFavoriteSelectionButton() {
  const count = selectedCount(activeSection);
  ui.favoriteSelection.textContent = count ? `收藏本次选择 · ${count}` : "收藏本次选择";
  ui.favoriteSelection.disabled = !favoritesAvailable || count === 0;
}
function normalizeTriggerWords(values) {
  const result = [];
  const seen = new Set();
  for (const value of Array.isArray(values) ? values : []) {
    const word = String(value || "").trim();
    const identity = word.toLocaleLowerCase();
    if (word && !seen.has(identity)) {
      result.push(word);
      seen.add(identity);
    }
  }
  return result;
}
function promptTokens(value) {
  return String(value || "")
    .replaceAll("\r", ",")
    .replaceAll("\n", ",")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
/**
 * 固定提示词自适应高度调整
 * @param {HTMLTextAreaElement} textarea
 */
function autoResizeFixedPrompt(textarea) {
  if (!textarea) return;
  // 先将高度重置为 auto，才能准确计算内容减少（删除文字）时的 scrollHeight
  textarea.style.height = "auto";
  // 加上边框容差，确保内容不出现意外微抖动
  textarea.style.height = `${Math.max(35, textarea.scrollHeight)}px`;
}
function triggerIdentity(value) {
  return String(value || "").trim().toLocaleLowerCase();
}
function forgetRemovedManagedTriggers() {
  const present = new Set(promptTokens(ui.extra_prompt.value).map(triggerIdentity));
  draft.managedTriggers = normalizeTriggerWords(
    (draft.managedTriggers || []).filter((word) => present.has(triggerIdentity(word))),
  );
}
function reconcileLoraTriggers(addFor = []) {
  if (!loraInventoryLoaded) return;
  const enabledItems = draft.loras.filter((item) => item.enabled);
  const metadataUnknown = enabledItems.some((item) => {
    const inventoryItem = loraItem(item.filename);
    return !inventoryItem || inventoryItem.trigger_metadata_available === false;
  });
  const current = promptTokens(ui.extra_prompt.value);
  const currentIds = new Set(current.map(triggerIdentity));
  const managed = new Map((draft.managedTriggers || []).map((word) => [triggerIdentity(word), word]));
  const required = new Set();
  for (const item of enabledItems) {
    const inventoryItem = loraItem(item.filename);
    for (const word of normalizeTriggerWords(inventoryItem?.trigger_words || [])) required.add(triggerIdentity(word));
  }
  for (const item of addFor) {
    if (!item.enabled) continue;
    const inventoryItem = loraItem(item.filename);
    for (const word of normalizeTriggerWords(inventoryItem?.trigger_words || [])) {
      const identity = triggerIdentity(word);
      required.add(identity);
      if (!currentIds.has(identity)) {
        current.push(word);
        currentIds.add(identity);
        managed.set(identity, word);
      }
    }
  }
  const keptManaged = [];
  for (const [identity, word] of managed) {
    if (required.has(identity) || metadataUnknown) keptManaged.push(word);
  }
  if (!metadataUnknown) {
    const removed = new Set(
      [...managed.keys()].filter((identity) => !required.has(identity)),
    );
    if (removed.size) {
      for (let index = current.length - 1; index >= 0; index--) {
        if (removed.has(triggerIdentity(current[index]))) current.splice(index, 1);
      }
    }
  }
  draft.managedTriggers = normalizeTriggerWords(keptManaged);
  const nextPrompt = current.join(", ");
  if (ui.extra_prompt.value !== nextPrompt) ui.extra_prompt.value = nextPrompt;
}
function loraItem(filename) {
  const identity = normalizedPath(filename);
  const exact = loraInventory.find((item) => normalizedPath(item.filename) === identity);
  if (exact) return exact;
  if (identity.includes("/")) return null;
  const matches = loraInventory.filter((item) => normalizedPath(item.filename).split("/").pop() === identity);
  return matches.length === 1 ? matches[0] : null;
}
function loraPresentation(inventoryItem, fallback) {
  const path = String(inventoryItem?.normalized_path || fallback || "").replaceAll("\\", "/");
  const parts = path.split("/").filter(Boolean);
  const fallbackBasename = parts.pop() || "未命名 LoRA";
  const fallbackFolder = parts.join("/");

  const basename = String(inventoryItem?.basename || fallbackBasename || "未命名 LoRA").trim();
  const rawFolder = inventoryItem && typeof inventoryItem.folder === "string"
    ? inventoryItem.folder.trim()
    : fallbackFolder;

  // 防御性判定：根目录或空目录不追加前缀，仅真实子目录才拼接层级
  const folder = (rawFolder && rawFolder !== "根目录") ? rawFolder : "";
  const label = folder ? `${folder} / ${basename}` : basename;
  return { path, basename, folder: folder || "根目录", label };
}
function renderLoras() {
  const loras = Array.isArray(draft.loras) ? draft.loras : [];
  const enabled = loras.filter((item) => item.enabled).length;
  ui.loraSummary.textContent = `${enabled} 启用 / ${loras.length} 配置`;
  ui.loraEmpty.hidden = loras.length > 0;
  ui.loraList.replaceChildren(
    ...loras.map((item, index) => {
      const available = !loraInventoryLoaded || Boolean(loraItem(item.filename));
      const high = Math.abs(Number(item.strength)) > 2;
      const row = document.createElement("div");
      row.className = `lora-row${available ? "" : " missing"}`;
      const inventoryItem = loraItem(item.filename);
      const display = loraPresentation(inventoryItem, item.filename);
      const triggers = normalizeTriggerWords(inventoryItem?.trigger_words || []);
      const triggerLabel = inventoryItem?.trigger_override ? "触发词（已覆盖）" : "触发词";
      const isSingleItem = loras.length <= 1;

      // 双层分工结构：第一行展示核心名称与开关/删除；第二行展示标签、触发词、权重与排序
      row.innerHTML = `
        <div class="lora-row-primary">
          <input class="lora-toggle" type="checkbox" ${item.enabled ? "checked" : ""} title="启用 LoRA" aria-label="启用 ${escapeHtml(item.filename)}">
          <div class="lora-name" title="${escapeHtml(display.path)}">
            <strong>${escapeHtml(display.label)}</strong>
          </div>
          <button class="icon-button dark lora-remove-btn" type="button" data-lora-remove title="移除" aria-label="移除">×</button>
        </div>
        <div class="lora-row-secondary">
          <div class="lora-tags">
            <small class="${available && !high ? "" : "lora-warning"}">${available ? (high ? "高强度 · 模型 + CLIP" : "模型 + CLIP") : "文件不存在"}</small>
            ${triggers.length || inventoryItem?.trigger_override ? `<small class="lora-trigger-line" title="自动触发词">${triggerLabel}：${triggers.length ? escapeHtml(triggers.join(", ")) : "已禁用"}</small>` : ""}
          </div>
          <div class="lora-actions">
            <button class="button ghost compact lora-trigger-edit" type="button" data-lora-triggers ${inventoryItem ? "" : "disabled"}>触发词</button>
            <input class="lora-strength" type="number" min="-100" max="100" step="0.05" value="${Number(item.strength)}" title="LoRA 权重" aria-label="${escapeHtml(item.filename)} 强度">
            <div class="lora-order-group" ${isSingleItem ? "hidden" : ""}>
              <button class="icon-button dark" type="button" data-lora-up title="上移" aria-label="上移">↑</button>
              <button class="icon-button dark" type="button" data-lora-down title="下移" aria-label="下移">↓</button>
            </div>
          </div>
        </div>
      `;

      row.querySelector(".lora-toggle")?.addEventListener("change", (event) => {
        item.enabled = event.target.checked;
        reconcileLoraTriggers(item.enabled ? [item] : []);
        renderLoras();
        schedulePersist();
      });

      row.querySelector(".lora-strength")?.addEventListener("change", (event) => {
        const value = Number(event.target.value);
        if (!Number.isFinite(value) || value < -100 || value > 100) {
          toast("LoRA strength 必须在 -100 到 100 之间");
          renderLoras();
          return;
        }
        item.strength = Math.round(value * 100) / 100;
        renderLoras();
        schedulePersist();
      });

      // 防御性可选链：保证即使单项隐藏按钮时也不会发生空指针报错
      const upBtn = row.querySelector("[data-lora-up]");
      const downBtn = row.querySelector("[data-lora-down]");
      if (upBtn) {
        upBtn.disabled = index === 0;
        upBtn.addEventListener("click", () => moveLora(index, -1));
      }
      if (downBtn) {
        downBtn.disabled = index === loras.length - 1;
        downBtn.addEventListener("click", () => moveLora(index, 1));
      }

      row.querySelector("[data-lora-triggers]")?.addEventListener("click", () => openLoraTriggerDialog(item));
      row.querySelector("[data-lora-remove]")?.addEventListener("click", () => {
        draft.loras.splice(index, 1);
        reconcileLoraTriggers();
        renderLoras();
        renderLoraCatalog();
        schedulePersist();
      });

      return row;
    }),
  );
}
function moveLora(index, delta) {
  const next = index + delta;
  if (next < 0 || next >= draft.loras.length) return;
  [draft.loras[index], draft.loras[next]] = [draft.loras[next], draft.loras[index]];
  renderLoras();
  schedulePersist();
}
async function loadLoraInventory() {
  try {
    const data = await request("/api/loras");
    loraInventory = data.items || [];
    loraInventoryLoaded = true;
    loraInventoryError = "";
    reconcileLoraTriggers(draft.loras.filter((item) => item.enabled));
    renderLoras();
    renderLoraCatalog();
  } catch (error) {
    loraInventoryLoaded = false;
    loraInventoryError = error.message;
    renderLoraCatalog();
  }
  updateRepairControls();
}
function renderLoraCatalog() {
  if (!ui.loraCatalog) return;
  const query = String(ui.loraSearch.value || "")
    .trim()
    .toLowerCase();
  const configured = new Set(
    draft.loras.map((item) => normalizedPath(loraItem(item.filename)?.filename || item.filename)),
  );
  const items = loraInventory.filter(
    (item) =>
      !query || `${item.normalized_path || item.filename} ${item.display_name || ""} ${(item.trigger_words || []).join(" ")}`.toLowerCase().includes(query),
  );
  ui.loraCatalogEmpty.hidden = Boolean(loraInventoryError) || items.length > 0;
  ui.loraCatalog.replaceChildren(
    ...items.map((item) => {
      const configuredItem = configured.has(normalizedPath(item.filename));
      const display = loraPresentation(item, item.filename);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "lora-catalog-item";
      button.disabled = configuredItem;
      const triggers = normalizeTriggerWords(item.trigger_words || []);
      const preview = item.preview
        ? `<img loading="lazy" decoding="async" src="${escapeHtml(item.preview)}" alt="" data-lora-preview>`
        : "";
      button.innerHTML = `<span class="lora-catalog-preview">${preview}<span class="lora-preview-placeholder" aria-hidden="true">LoRA</span></span><span class="lora-catalog-copy"><strong title="${escapeHtml(item.display_name || display.path)}">${escapeHtml(item.display_name || display.basename)}</strong><small title="${escapeHtml(display.path)}">${escapeHtml(display.folder)} / ${escapeHtml(display.basename)}${configuredItem ? " · 已配置" : ""}</small><span class="lora-catalog-triggers">${item.trigger_override ? "已覆盖 · " : ""}${triggers.length ? `触发词：${escapeHtml(triggers.join(", "))}` : item.trigger_override ? "已禁用触发词" : "无触发词"}</span></span><span class="lora-catalog-add" aria-hidden="true">${configuredItem ? "✓" : "+"}</span>`;
      button.querySelector("[data-lora-preview]")?.addEventListener("error", (event) => {
        event.currentTarget.remove();
      });
      button.addEventListener("click", () => {
        const lora = { filename: item.filename, enabled: true, strength: 1 };
        draft.loras.push(lora);
        reconcileLoraTriggers([lora]);
        renderLoras();
        renderLoraCatalog();
        schedulePersist();
      });
      return button;
    }),
  );
  ui.loraCatalogMeta.textContent = loraInventoryError || `${loraInventory.length} 个本地 LoRA`;
}
async function openLoraDialog() {
  ui.loraSearch.value = "";
  renderLoraCatalog();
  ui.loraDialog.showModal();
  await loadLoraInventory();
  renderLoraCatalog();
}
function parseLoraTriggerInput(value) {
  return normalizeTriggerWords(
    String(value || "")
      .replaceAll("\r", ",")
      .replaceAll("\n", ",")
      .replaceAll("，", ",")
      .split(","),
  );
}
function replaceLoraInventoryItem(value) {
  const identity = normalizedPath(value.filename);
  const index = loraInventory.findIndex((item) => normalizedPath(item.filename) === identity);
  if (index >= 0) loraInventory[index] = value;
  else loraInventory.push(value);
}
function openLoraTriggerDialog(configuredItem) {
  const inventoryItem = loraItem(configuredItem.filename);
  if (!inventoryItem) return;
  editingLoraTrigger = configuredItem;
  const display = loraPresentation(inventoryItem, configuredItem.filename);
  ui.loraTriggerTitle.textContent = `编辑 ${inventoryItem.display_name || display.basename}`;
  ui.loraTriggerFilename.value = inventoryItem.filename;
  ui.loraTriggerWords.value = normalizeTriggerWords(inventoryItem.trigger_words || []).join("\n");
  const source = normalizeTriggerWords(inventoryItem.source_trigger_words || []);
  ui.loraSourceTriggerWords.textContent = source.length ? source.join(", ") : "无";
  ui.resetLoraTriggers.disabled = !inventoryItem.trigger_override;
  ui.loraTriggerDialog.showModal();
}
async function saveLoraTriggers(event) {
  event.preventDefault();
  if (!editingLoraTrigger) return;
  try {
    const value = await request("/api/loras/triggers", {
      method: "PUT",
      body: JSON.stringify({
        filename: ui.loraTriggerFilename.value,
        triggerWords: parseLoraTriggerInput(ui.loraTriggerWords.value),
      }),
    });
    replaceLoraInventoryItem(value);
    reconcileLoraTriggers(editingLoraTrigger.enabled ? [editingLoraTrigger] : []);
    renderLoras();
    renderLoraCatalog();
    schedulePersist();
    ui.loraTriggerDialog.close();
    toast(value.trigger_words?.length ? "LoRA 触发词已保存" : "已禁用该 LoRA 的自动触发词");
  } catch (error) {
    toast(error.message);
  }
}
async function resetLoraTriggers() {
  if (!editingLoraTrigger) return;
  try {
    const filename = encodeURIComponent(ui.loraTriggerFilename.value);
    const value = await request(`/api/loras/triggers?filename=${filename}`, { method: "DELETE" });
    replaceLoraInventoryItem(value);
    reconcileLoraTriggers(editingLoraTrigger.enabled ? [editingLoraTrigger] : []);
    renderLoras();
    renderLoraCatalog();
    schedulePersist();
    ui.loraTriggerDialog.close();
    toast("已恢复 LoRA Manager 原始触发词");
  } catch (error) {
    toast(error.message);
  }
}

let currentQueue = [];
let lastPreviewId = 0;
let submitInFlight = false;
function renderBatchPayload(payload) {
  renderBatch(payload.batch, payload.queue || []);
}
let queuePanelCloseTimer = null;
function setQueuePanelOpen(open) {
  if (!ui.queuePanel) return;
  clearTimeout(queuePanelCloseTimer);
  if (open) {
    ui.queuePanel.hidden = false;
    // Force a frame so the transition plays from the collapsed style.
    ui.queuePanel.getBoundingClientRect();
    ui.queuePanel.classList.add("open");
  } else {
    ui.queuePanel.classList.remove("open");
    queuePanelCloseTimer = setTimeout(() => { ui.queuePanel.hidden = true; }, 320);
  }
}

function renderQueue(queue) {
  currentQueue = queue;
  if (!ui.queueBadge || !ui.queuePanel) return;
  ui.queueBadge.hidden = queue.length === 0;
  ui.queueBadge.textContent = `队列 ${queue.length}`;
  if (queue.length === 0) {
    setQueuePanelOpen(false);
  }
  ui.queuePanel.replaceChildren(
    ...queue.map((entry) => {
      const row = document.createElement("div");
      row.className = "queue-row";
      const label = document.createElement("span");
      label.textContent = `${entry.position}. ${entry.count} 张 · ${entry.model_name}`;
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "icon-button dark";
      remove.title = "移出队列";
      remove.setAttribute("aria-label", "移出队列");
      remove.textContent = "×";
      remove.addEventListener("click", async () => {
        try {
          const payload = await request(`/api/batches/queue/${entry.queue_id}`, { method: "DELETE" });
          renderQueue(payload.queue || []);
        } catch (error) {
          toast(error.message);
        }
      });
      row.append(label, remove);
      return row;
    }),
  );
}
function renderBatch(batch, queue = currentQueue) {
  currentBatch = batch;
  renderQueue(queue);
  const active = Boolean(batch && ["running", "stopping"].includes(batch.status));
  const completed = batch?.completed || 0;
  const total = batch?.total || 0;
  const labels = {
    running: "正在生成",
    stopping: "完成当前张后停止",
    completed: "批次完成",
    stopped: "已停止",
    error: "执行失败",
  };
  ui.batchState.textContent = batch ? labels[batch.status] || batch.status : "等待任务";
  ui.progressCount.textContent = `${completed} / ${total}`;
  ui.progressFill.style.width = total ? `${Math.min(100, (completed / total) * 100)}%` : "0%";
  // 单张采样进度(来自 ComfyUI websocket,尽力而为;旧版页面缺控件时跳过)
  if (ui.sampleFill && ui.sampleProgress) {
    const progress = active ? batch.progress : null;
    const sampleTrack = ui.sampleFill.parentElement;
    if (progress && progress.max > 0) {
      ui.sampleProgress.hidden = false;
      ui.sampleProgress.textContent = `采样 ${progress.value}/${progress.max}`;
      sampleTrack.hidden = false;
      ui.sampleFill.style.width = `${Math.min(100, (progress.value / progress.max) * 100)}%`;
    } else {
      ui.sampleProgress.hidden = true;
      sampleTrack.hidden = true;
      ui.sampleFill.style.width = "0%";
    }
  }
  // 实时预览帧:preview_id 变化时刷新缩略图
  if (ui.livePreview) {
    if (active && batch.preview_id && batch.preview_id !== lastPreviewId) {
      lastPreviewId = batch.preview_id;
      ui.livePreview.src = `/api/batches/current/preview?v=${batch.preview_id}`;
      ui.livePreview.hidden = false;
    } else if (!active) {
      ui.livePreview.hidden = true;
      lastPreviewId = 0;
    }
  }
  ui.stopButton.disabled = !active || batch.status === "stopping";
  // 队列时代:运行中也允许点"开始"(进入队列),只受连接与在途请求限制
  ui.startButton.disabled = submitInFlight || !ui.connection.classList.contains("online");
  ui.startButton.textContent = active ? "加入队列" : "开始生成";
  ui.batchError.hidden = !batch?.error;
  ui.batchError.textContent = batch?.error || "";
  if (batch && !active && lastTerminalBatch !== `${batch.id}:${batch.status}:${completed}`) {
    lastTerminalBatch = `${batch.id}:${batch.status}:${completed}`;
    loadHistory(1);
    // 批次结束后新图片已入库,同步刷新胶囊栏计数。
    loadGalleryCollections();
  }
}
async function refreshConnection() {
  if (document.hidden) return;
  try {
    const status = await request("/api/status");
    ui.connection.className = `status-badge ${status.online ? "online" : "offline"}`;
    ui.connection.querySelector("span").textContent = status.online ? `ComfyUI ${status.version}` : "ComfyUI 离线";
    ui.startButton.disabled = submitInFlight || !status.online;
  } catch {
    ui.connection.className = "status-badge offline";
    ui.connection.querySelector("span").textContent = "ComfyUI 离线";
    ui.startButton.disabled = true;
  }
}
let pollErrorShown = false;
let pollIdleTicks = 0;
async function pollBatch() {
  // 后台标签页不轮询;空闲(无运行中批次)时降频到约 1/4,避免常开高频请求。
  if (document.hidden) return;
  const batchActive = Boolean(currentBatch && ["running", "stopping"].includes(currentBatch.status));
  if (!batchActive && pollIdleTicks++ % 4 !== 0) return;
  try {
    renderBatchPayload(await request("/api/batches/current"));
    pollErrorShown = false;
  } catch (error) {
    // 服务端不可达时只提示一次,恢复后自动复位,不再每 1.2 秒刷屏。
    if (!pollErrorShown) {
      toast(error.message);
      pollErrorShown = true;
    }
  }
}
const DEFAULT_COLLECTION_ID = 1;

function isDefaultFavorite(record) {
  const ids = Array.isArray(record?.collection_ids) ? record.collection_ids : [];
  return ids.some((value) => Number(value) === DEFAULT_COLLECTION_ID);
}

// 同步本地分页缓存中的收藏状态,避免翻页后星标回退成旧值。
function syncCachedCollections(imageId, collectionIds) {
  const target = Number(imageId);
  const ids = Array.isArray(collectionIds) ? collectionIds.map(Number) : [];
  for (const data of historyCache.values()) {
    const items = Array.isArray(data?.items) ? data.items : [];
    for (const item of items) {
      if (Number(item?.id) === target) item.collection_ids = [...ids];
    }
  }
  if (Array.isArray(historyItems)) {
    for (const item of historyItems) {
      if (Number(item?.id) === target) item.collection_ids = [...ids];
    }
  }
  if (selectedRecord && Number(selectedRecord.id) === target) {
    selectedRecord.collection_ids = [...ids];
  }
}

// 就地刷新当前画廊中该作品的星标(不重建卡片,避免布局跳动)。
function paintCardFavorite(imageId, favorite) {
  const target = String(imageId);
  for (const star of ui.gallery.querySelectorAll(".image-favorite-star")) {
    if (star.dataset.imageId !== target) continue;
    paintFavoriteStar(star, favorite);
  }
}

// 收藏夹徽标计数增量更新:delta 为 +1/-1,避免每次点星都全量拉取。
function adjustCollectionCount(collectionId, delta) {
  const target = Number(collectionId);
  if (!Number.isFinite(target) || !delta) return;
  const collection = galleryCollections.find((item) => Number(item.id) === target);
  if (!collection) return;
  collection.item_count = Math.max(0, Number(collection.item_count || 0) + delta);
  renderGalleryCollections();
}

function paintFavoriteStar(star, favorite) {
  star.dataset.favorite = favorite ? "true" : "false";
  star.setAttribute("aria-pressed", favorite ? "true" : "false");
  star.title = favorite ? "取消收藏" : "收藏";
}

async function toggleDefaultFavorite(record, star) {
  const previous = isDefaultFavorite(record);
  const optimistic = !previous;
  // 乐观更新:先点亮/熄灭并播放微弹跳,再等待服务端确认。
  paintFavoriteStar(star, optimistic);
  star.classList.remove("is-popping");
  void star.offsetWidth;
  star.classList.add("is-popping");
  try {
    const result = await request(`/api/history/${record.id}/toggle-default-favorite`, {
      method: "POST",
    });
    const favorite = Boolean(result?.is_favorite);
    const ids = Array.isArray(result?.collection_ids) ? result.collection_ids : [];
    paintFavoriteStar(star, favorite);
    syncCachedCollections(record.id, ids);
    // 顶部“默认收藏”胶囊徽标即时 +1/-1;当前视图中的卡片保持原地,仅星标置灰。
    if (favorite !== previous) adjustCollectionCount(DEFAULT_COLLECTION_ID, favorite ? 1 : -1);
  } catch (error) {
    // 失败回滚:恢复点击前的星标状态,并提示原因。
    paintFavoriteStar(star, previous);
    toast(error.message);
  }
}

// ---------- 批量管理:状态机与选择逻辑 ----------
// 设计要点:
// 1) isBatchMode 为唯一模式开关,所有入口(按钮/卡片/复选框)都经由 setBatchMode 收敛;
// 2) selectedBatchIds 跨页保留,但只对当前页可见卡片做视觉同步,避免误删不可见项;
// 3) Shift 连选以 lastBatchAnchorId 为锚点,在当前页顺序内做闭区间选择。

function batchCardElements() {
  if (!ui.gallery) return [];
  return [...ui.gallery.querySelectorAll(".image-card")];
}

// 当前页可见的作品 id 顺序(与 DOM 顺序一致,保证 Shift 区间语义正确)。
function batchPageIds() {
  return batchCardElements()
    .map((element) => Number(element.dataset.imageId))
    .filter((value) => Number.isFinite(value) && value > 0);
}

function paintBatchCard(article, imageId) {
  if (!article) return;
  const selected = selectedBatchIds.has(Number(imageId));
  article.classList.toggle("is-selected", selected);
  const check = article.querySelector(".batch-check");
  if (check) {
    check.setAttribute("aria-checked", selected ? "true" : "false");
    check.title = selected ? "取消选择" : "选择此作品";
  }
}

// 就地刷新所有卡片的选中态,不重建 DOM(避免图片重新加载与布局跳动)。
function paintBatchSelection() {
  for (const article of batchCardElements()) {
    paintBatchCard(article, Number(article.dataset.imageId));
  }
  updateBatchActionBar();
}

function updateBatchActionBar() {
  const count = selectedBatchIds.size;
  if (ui.batchSelectedCount) ui.batchSelectedCount.textContent = String(count);
  const pageIds = batchPageIds();
  const allSelected = pageIds.length > 0 && pageIds.every((id) => selectedBatchIds.has(id));
  if (ui.batchSelectAll) {
    ui.batchSelectAll.textContent = allSelected ? "取消全选" : "全选本页";
    ui.batchSelectAll.disabled = pageIds.length === 0;
    ui.batchSelectAll.setAttribute("aria-pressed", allSelected ? "true" : "false");
  }
  const empty = count === 0;
  for (const button of [ui.batchExport, ui.batchFavorite, ui.batchDelete]) {
    if (button) button.disabled = empty || batchBusy;
  }
  if (ui.batchClearSelection) ui.batchClearSelection.disabled = empty || batchBusy;
  if (ui.batchExit) ui.batchExit.disabled = batchBusy;
  if (ui.batchActionBar) ui.batchActionBar.classList.toggle("is-busy", batchBusy);
}

function showBatchActionBar() {
  if (!ui.batchActionBar) return;
  clearTimeout(batchBarHideTimer);
  ui.batchActionBar.hidden = false;
  ui.batchActionBar.classList.remove("is-leaving");
  ui.batchActionBar.setAttribute("aria-hidden", "false");
  // 重新触发入场动画(隐藏后再次显示时 CSS 动画不会自动重播)。
  void ui.batchActionBar.offsetWidth;
}

function hideBatchActionBar() {
  if (!ui.batchActionBar || ui.batchActionBar.hidden) return;
  ui.batchActionBar.setAttribute("aria-hidden", "true");
  if (imagePreviewReducedMotion()) {
    ui.batchActionBar.hidden = true;
    return;
  }
  ui.batchActionBar.classList.add("is-leaving");
  clearTimeout(batchBarHideTimer);
  batchBarHideTimer = setTimeout(() => {
    ui.batchActionBar.hidden = true;
    ui.batchActionBar.classList.remove("is-leaving");
  }, 230);
}

function setBatchMode(enabled) {
  const next = Boolean(enabled);
  if (next === isBatchMode) return;
  isBatchMode = next;
  // 全局状态类名,便于样式级联(如 body.is-batch-mode .command-deck)。
  document.body.classList.toggle("is-batch-mode", isBatchMode);
  // 生图控制台与批量操作栏互斥:批量模式下平滑下移收起,退出时复位。
  const deck = ui.commandDeck || document.querySelector(".command-deck");
  if (deck) {
    deck.classList.toggle("is-batch-hidden", isBatchMode);
    deck.setAttribute("aria-hidden", String(isBatchMode));
  }
  if (ui.gallery) ui.gallery.classList.toggle("is-batch-mode", isBatchMode);
  if (ui.btnToggleBatchMode) {
    ui.btnToggleBatchMode.setAttribute("aria-pressed", isBatchMode ? "true" : "false");
    ui.btnToggleBatchMode.title = isBatchMode ? "退出批量管理" : "批量管理作品";
    const label = ui.btnToggleBatchMode.querySelector("span");
    if (label) label.textContent = isBatchMode ? "退出批量" : "批量管理";
  }
  if (isBatchMode) {
    showBatchActionBar();
    paintBatchSelection();
  } else {
    // 退出时清空选择并复位锚点,避免下次进入残留旧状态。
    selectedBatchIds.clear();
    lastBatchAnchorId = null;
    // 批量弹窗若仍打开,一并复位关闭,避免上下文悬挂。
    if (batchFavoriteContext && ui.imageCollectionsDialog?.open) closeBatchFavoriteDialog();
    if (batchDeleteContext && ui.recordDeleteDialog?.open) closeBatchDeleteDialog();
    paintBatchSelection();
    hideBatchActionBar();
  }
}

function toggleBatchSelection(imageId, { shiftKey = false } = {}) {
  const target = Number(imageId);
  if (!Number.isFinite(target) || target <= 0) return;
  if (!isBatchMode) setBatchMode(true);

  if (shiftKey && lastBatchAnchorId !== null) {
    const pageIds = batchPageIds();
    const from = pageIds.indexOf(lastBatchAnchorId);
    const to = pageIds.indexOf(target);
    if (from >= 0 && to >= 0) {
      // 区间连选:以锚点当前状态为准,整段统一为“选中”或“取消”。
      const shouldSelect = !selectedBatchIds.has(target);
      const [start, end] = from <= to ? [from, to] : [to, from];
      for (let index = start; index <= end; index += 1) {
        if (shouldSelect) selectedBatchIds.add(pageIds[index]);
        else selectedBatchIds.delete(pageIds[index]);
      }
      lastBatchAnchorId = target;
      paintBatchSelection();
      return;
    }
  }

  if (selectedBatchIds.has(target)) selectedBatchIds.delete(target);
  else selectedBatchIds.add(target);
  lastBatchAnchorId = target;
  paintBatchSelection();
}

function selectAllBatchPage() {
  const pageIds = batchPageIds();
  if (!pageIds.length) return;
  const allSelected = pageIds.every((id) => selectedBatchIds.has(id));
  for (const id of pageIds) {
    if (allSelected) selectedBatchIds.delete(id);
    else selectedBatchIds.add(id);
  }
  lastBatchAnchorId = allSelected ? null : pageIds[pageIds.length - 1];
  paintBatchSelection();
}

function clearBatchSelection() {
  selectedBatchIds.clear();
  lastBatchAnchorId = null;
  paintBatchSelection();
}

// 批量请求统一入口:锁定操作条、串行执行、结束后刷新选择态。
// 失败时优先回显到调用方指定的弹窗错误区(如批量删除/收藏弹窗),否则退化为 toast。
async function runBatchTask(task, { onError } = {}) {
  if (batchBusy) return;
  batchBusy = true;
  updateBatchActionBar();
  try {
    await task();
  } catch (error) {
    const message = error?.message || "批量操作失败";
    if (typeof onError === "function") onError(message);
    else toast(message);
  } finally {
    batchBusy = false;
    updateBatchActionBar();
  }
}

// 批量导出前自动检测导出目录:本地缓存为空时先向后端拉取一次,
// 仍未配置才唤起系统选目录弹窗,避免“已配置却误提示未设置”。
async function ensureBatchExportFolder() {
  if (currentExportFolder) return true;
  try {
    const data = await request("/api/settings/export-folder");
    currentExportFolder = data?.export_dir || "";
    renderExportFolderWidget();
  } catch (error) {
    console.error("检测导出目录失败:", error);
  }
  if (currentExportFolder) return true;
  toast("尚未配置导出目录，请先选择目标文件夹");
  return triggerPickExportFolder();
}

async function batchExportSelected() {
  const ids = [...selectedBatchIds];
  if (!ids.length || batchBusy) return;
  const ready = await ensureBatchExportFolder();
  if (!ready) return;
  await runBatchTask(async () => {
    const result = await request("/api/history/batch-export", {
      method: "POST",
      body: JSON.stringify({ image_ids: ids }),
    });
    const exported = Number(result?.exported_count || 0);
    const failed = Number(result?.failed_count || 0);
    if (!exported && failed) {
      toast(`导出失败：${failed} 张作品均未能导出`);
      return;
    }
    toast(
      failed
        ? `已导出 ${exported} 张，${failed} 张失败`
        : `已导出 ${exported} 张到 ${result?.folder_name || "导出目录"}`,
    );
  });
}

// ---------- 批量收藏:复用 #imageCollectionsDialog ----------
// batchFavoriteContext 非空时,弹窗进入“批量模式”:勾选状态取所选作品的交集,
// 保存时调用 /api/history/batch-collections 的 set 模式统一覆盖归属。
let batchFavoriteContext = null;

function batchSelectedRecords() {
  const wanted = new Set([...selectedBatchIds].map(Number));
  return historyItems.filter((item) => wanted.has(Number(item.id)));
}

function openBatchFavoriteDialog() {
  const records = batchSelectedRecords();
  if (!records.length) {
    toast("请先选择要收藏的作品");
    return;
  }
  batchFavoriteContext = { ids: records.map((item) => Number(item.id)) };
  setImageCollectionsError("");
  if (ui.newCollectionNameInput) ui.newCollectionNameInput.value = "";
  // 交集语义:仅当所有选中作品都已在某收藏夹时才默认勾选,避免误覆盖。
  const intersection = records.reduce((acc, record) => {
    const ids = new Set(
      (Array.isArray(record.collection_ids) ? record.collection_ids : []).map(Number),
    );
    return acc === null ? ids : new Set([...acc].filter((id) => ids.has(id)));
  }, null);
  renderImageCollectionsChecklist([...(intersection || [])]);
  const hint = ui.imageCollectionsDialog?.querySelector(".import-hint");
  if (hint) hint.textContent = `已选 ${records.length} 张作品，勾选要归入的收藏夹（保存后将覆盖这些作品的收藏归属）：`;
  // 批量模式语义是“归属管理”,标题需与单图“添加到收藏夹”区分。
  const title = ui.imageCollectionsDialog?.querySelector(".dialog-heading h2");
  if (title) title.textContent = "管理收藏归属";
  // 依据交集勾选结果初始化警告与保存按钮状态。
  updateBatchCollectionsState();
  ui.imageCollectionsDialog.showModal();
}

function closeBatchFavoriteDialog() {
  batchFavoriteContext = null;
  const hint = ui.imageCollectionsDialog?.querySelector(".import-hint");
  if (hint) hint.textContent = "勾选此作品加入的收藏夹，可同时归入多个分类：";
  const title = ui.imageCollectionsDialog?.querySelector(".dialog-heading h2");
  if (title) title.textContent = "添加到收藏夹";
  // 复位警告与按钮,避免污染后续单图收藏界面。
  resetBatchCollectionsState();
  ui.imageCollectionsDialog.close();
}

// 批量模式下的警告与保存按钮联动:未勾选任何收藏夹时提示“移出全部收藏”并切换危险态。
function updateBatchCollectionsState() {
  if (!batchFavoriteContext) return;
  const warning = ui.imageCollectionsBatchWarning || document.getElementById("imageCollectionsBatchWarning");
  const saveBtn = ui.saveImageCollections;
  const clearing = checkedImageCollectionIds().length === 0;

  if (warning) warning.hidden = !clearing;
  if (saveBtn) {
    saveBtn.textContent = clearing ? "移出全部收藏" : "保存";
    saveBtn.classList.toggle("danger", clearing);
    saveBtn.classList.toggle("primary", !clearing);
  }
}

function resetBatchCollectionsState() {
  const warning = ui.imageCollectionsBatchWarning || document.getElementById("imageCollectionsBatchWarning");
  const saveBtn = ui.saveImageCollections;
  if (warning) warning.hidden = true;
  if (saveBtn) {
    saveBtn.textContent = "保存";
    saveBtn.classList.remove("danger");
    saveBtn.classList.add("primary");
  }
}

async function saveBatchImageCollections() {
  const context = batchFavoriteContext;
  if (!context || imageCollectionsSaving) return;
  const collectionIds = checkedImageCollectionIds();
  // 后端 set 模式拒绝空 collection_ids:全部取消勾选时改用 remove 逐个清空,
  // 语义等价于“把这些作品移出所有收藏夹”。二次确认已由弹窗内联警告与危险按钮承担。
  const clearing = collectionIds.length === 0;
  imageCollectionsSaving = true;
  if (ui.saveImageCollections) ui.saveImageCollections.disabled = true;
  setImageCollectionsError("");
  try {
    const result = await request("/api/history/batch-collections", {
      method: "POST",
      body: JSON.stringify({
        image_ids: context.ids,
        collection_ids: clearing
          ? galleryCollections.map((item) => Number(item.id)).filter((id) => id > 0)
          : collectionIds,
        mode: clearing ? "remove" : "set",
      }),
    });
    const updated = Array.isArray(result?.updated) ? result.updated.map(Number) : context.ids;
    // 本地缓存与卡片星标同步,避免等待整页重载。
    for (const id of updated) {
      syncCachedCollections(id, collectionIds);
      paintCardFavorite(id, collectionIds.includes(DEFAULT_COLLECTION_ID));
    }
    closeBatchFavoriteDialog();
    // 全库数量与各收藏夹徽标必须全量刷新:set/remove 可能同时影响多个收藏夹。
    await loadGalleryCollections();
    // 当前正停留在某个收藏夹视图时,归属变化会让列表内容失效,需重新拉取。
    if (activeCollectionId !== 0) await loadHistory(historyPage);
    toast(
      clearing
        ? `已将 ${updated.length} 张作品移出全部收藏夹`
        : `已更新 ${updated.length} 张作品的收藏归属`,
    );
  } catch (error) {
    setImageCollectionsError(error.message || "批量收藏失败");
  } finally {
    imageCollectionsSaving = false;
    if (ui.saveImageCollections) ui.saveImageCollections.disabled = false;
  }
}

// ---------- 批量删除:复用 #recordDeleteDialog ----------
let batchDeleteContext = null;

function setRecordDeleteError(message = "") {
  if (!ui.recordDeleteError) return;
  ui.recordDeleteError.textContent = message;
  ui.recordDeleteError.hidden = !message;
}

function openBatchDeleteDialog() {
  const ids = [...selectedBatchIds];
  if (!ids.length) {
    toast("请先选择要删除的作品");
    return;
  }
  batchDeleteContext = { ids };
  ui.recordDeleteSummary.textContent = `已选 ${ids.length} 张作品`;
  const warning = ui.recordDeleteDialog?.querySelector(".record-delete-warning");
  if (warning) {
    warning.textContent = `⚠️ 确定要删除已选的 ${ids.length} 张作品吗？此操作将同步永久删除本地物理图片文件，不可撤销。`;
  }
  const title = ui.recordDeleteDialog?.querySelector(".dialog-heading h2");
  if (title) title.textContent = "批量删除作品";
  setRecordDeleteError("");
  ui.confirmRecordDelete.disabled = false;
  ui.confirmRecordDelete.textContent = "确认删除";
  ui.recordDeleteDialog.showModal();
}

function closeBatchDeleteDialog() {
  batchDeleteContext = null;
  const warning = ui.recordDeleteDialog?.querySelector(".record-delete-warning");
  if (warning) {
    warning.textContent = "⚠️ 确定要删除该作品吗？此操作将同步永久删除本地物理图片文件，不可撤销。";
  }
  const title = ui.recordDeleteDialog?.querySelector(".dialog-heading h2");
  if (title) title.textContent = "删除作品";
  ui.recordDeleteDialog.close();
}

async function submitBatchDelete() {
  const context = batchDeleteContext;
  if (!context || ui.confirmRecordDelete.disabled) return;
  const ids = [...context.ids];
  ui.confirmRecordDelete.disabled = true;
  ui.confirmRecordDelete.textContent = "正在删除...";
  setRecordDeleteError("");
  await runBatchTask(
    async () => {
      const result = await request("/api/history/batch-delete", {
        method: "POST",
        body: JSON.stringify({ image_ids: ids }),
      });
      // 后端 deleted 为实际删除的记录行数(整数),兼容旧版数组返回。
      const deleted = Array.isArray(result?.deleted)
        ? result.deleted.length
        : Number(result?.deleted ?? ids.length);
      for (const id of ids) selectedBatchIds.delete(Number(id));
      lastBatchAnchorId = null;
      closeBatchDeleteDialog();
      // 删除后当前页可能已空:先按剩余数量推算目标页,再由后端 pages 兜底校正。
      const remaining = Math.max(0, historyItems.length - deleted);
      const targetPage = remaining === 0 && historyPage > 1 ? historyPage - 1 : historyPage;
      await loadHistory(targetPage);
      // 若目标页仍越界(跨页选择导致删空多页),继续向前回退直到有内容或到第 1 页。
      // 每轮必须严格递减页码,避免请求失败时 historyPage 不变导致死循环。
      let guard = historyPages + 1;
      while (historyItems.length === 0 && historyPage > 1 && guard-- > 0) {
        const previousPage = historyPage - 1;
        await loadHistory(previousPage);
        if (historyPage >= previousPage) break;
      }
      await loadGalleryCollections();
      paintBatchSelection();
      toast(`已删除 ${deleted} 张作品`);
    },
    {
      onError: (message) => {
        // 文件锁等致命错误:整批未提交,弹窗保持打开并回显原因。
        setRecordDeleteError(message);
      },
    },
  );
  ui.confirmRecordDelete.disabled = false;
  ui.confirmRecordDelete.textContent = "确认删除";
}

function card(record, index) {
  const article = document.createElement("article");
  article.className = "image-card is-loading";
  article.dataset.imageId = String(record.id);
  article.style.animationDelay = `${Math.min(index * 25, 250)}ms`;
  const button = document.createElement("button");
  button.type = "button";
  button.setAttribute("aria-label", `查看 ${record.filename || "生成结果"}`);
  button.innerHTML = `<img loading="lazy" decoding="async" fetchpriority="low" src="/api/images/${record.id}" alt="Anima 生成结果"><span class="image-failure" hidden>图片加载失败</span><div class="card-copy"><div class="card-copy-text"><strong>${escapeHtml(record.filename)}</strong><span>#${record.sequence} · Seed ${record.sample_seed}</span></div><button type="button" class="image-favorite-star" aria-pressed="false" title="收藏">★</button></div>`;
  button.addEventListener("click", (event) => {
    // 批量模式下点击卡片 = 切换勾选,绝不弹出详情弹窗。
    if (isBatchMode) {
      event.preventDefault();
      toggleBatchSelection(record.id, { shiftKey: event.shiftKey });
      return;
    }
    openDetail(record);
  });
  // 复选框是卡片按钮内的独立控件:阻止冒泡,避免重复触发卡片点击逻辑。
  const check = document.createElement("button");
  check.type = "button";
  check.className = "batch-check";
  check.setAttribute("role", "checkbox");
  check.setAttribute("aria-checked", "false");
  check.setAttribute("aria-label", `选择 ${record.filename || "生成结果"}`);
  check.tabIndex = -1;
  check.addEventListener("click", (event) => {
    event.stopPropagation();
    event.preventDefault();
    toggleBatchSelection(record.id, { shiftKey: event.shiftKey });
  });
  article.append(check);
  paintBatchCard(article, record.id);
  const star = button.querySelector(".image-favorite-star");
  star.dataset.imageId = String(record.id);
  paintFavoriteStar(star, isDefaultFavorite(record));
  star.addEventListener("click", (event) => {
    // 星标是卡片按钮内的独立控件:必须阻止冒泡,否则会打开详情弹窗。
    event.stopPropagation();
    event.preventDefault();
    toggleDefaultFavorite(record, star);
  });
  // 指针按下阶段即拦截,避免事件穿透到外层卡片按钮触发详情。
  star.addEventListener("pointerdown", (event) => {
    event.stopPropagation();
  });
  star.addEventListener("mousedown", (event) => {
    event.stopPropagation();
  });
  const image = button.querySelector("img");
  const markLoaded = () => {
    article.classList.remove("is-loading");
    image.classList.add("image-loaded");
  };
  image.addEventListener("load", markLoaded, { once: true });
  const markFailed = (event) => {
    article.classList.remove("is-loading");
    event?.target?.classList.add("image-failed");
    button.querySelector(".image-failure").hidden = false;
  };
  image.addEventListener("error", markFailed, { once: true });
  if (image.complete) {
    if (image.naturalWidth) markLoaded();
    else markFailed({ target: image });
  }
  article.append(button);
  return article;
}
let historyRequest = 0;
// 缓存 Key 必须包含收藏夹维度,否则“全部”与各收藏夹的分页数据会互相覆盖。
function historyCacheKey(page, collectionId = activeCollectionId) {
  return `${Number(collectionId) || 0}_${Number(page) || 1}`;
}

function cacheHistoryPage(data, collectionId = activeCollectionId) {
  if (!data || !Number.isFinite(Number(data.page))) return;
  historyCache.set(historyCacheKey(data.page, collectionId), data);
}

function cachedHistoryPage(page, collectionId = activeCollectionId) {
  return historyCache.get(historyCacheKey(page, collectionId)) || null;
}

function renderHistoryPage(data) {
  historyPage = Number(data.page) || 1;
  historyPages = Number(data.pages) || 1;
  historyItems = Array.isArray(data.items) ? data.items : [];
  cacheHistoryPage(data);
  ui.gallery.replaceChildren(...historyItems.map(card));
  ui.emptyState.hidden = historyItems.length > 0;
  // 空状态文案按当前视图区分:收藏夹为空与全库为空语义不同。
  if (ui.emptyState && historyItems.length === 0) {
    const title = ui.emptyState.querySelector("strong");
    const hint = ui.emptyState.querySelector("small");
    if (activeCollectionId === 0) {
      if (title) title.textContent = "等待第一张作品";
      if (hint) hint.textContent = "完成生成后会出现在这里";
    } else {
      if (title) title.textContent = "这个收藏夹还是空的";
      if (hint) hint.textContent = "在作品详情中点击“收藏至...”即可加入";
    }
  }
  ui.pageLabel.textContent = `${historyPage} / ${historyPages}`;
  ui.prevPage.disabled = historyPage <= 1;
  ui.nextPage.disabled = historyPage >= historyPages;
  ui.historyCount.textContent = `${data.total || 0} 张图片`;
  ui.galleryCount.textContent = String(data.total || 0);
  // 历史列表分页更新(生图完成、翻页、删除)时,同步“全部”胶囊徽标。
  const allPillBadge = document.querySelector("#galleryCollectionsBar .pill-all .pill-badge");
  if (allPillBadge && activeCollectionId === 0) {
    allPillBadge.textContent = String(data.total || 0);
  }
  updatePreviewNavigation();
  updateDetailNavigation();
  // 翻页/刷新后重新同步批量模式视觉状态:选择集合跨页保留,但只高亮当前页可见项。
  if (isBatchMode) {
    ui.gallery.classList.add("is-batch-mode");
    paintBatchSelection();
  }
}

async function loadHistory(page = historyPage) {
  // 与 loadPool 相同的竞态守卫:快速翻页时丢弃乱序到达的旧响应。
  const requestId = ++historyRequest;
  const collectionId = activeCollectionId;
  try {
    const data = await request(
      `/api/history?page=${page}&limit=24&collection_id=${collectionId}`,
    );
    if (requestId !== historyRequest) return;
    // “全部”视图的总数即全库总数,顺手同步胶囊数据源,保证翻页/生图后徽标一致。
    if (collectionId === 0 && Number.isFinite(Number(data?.total))) {
      galleryAllTotal = Math.max(0, Number(data.total));
    }
    renderHistoryPage(data);
  } catch (error) {
    if (requestId !== historyRequest) return;
    toast(error.message);
  }
}

// ---------- 收藏夹胶囊栏通用交互:滚轮横向桥接 / 溢出遮罩 / 新建后聚焦 ----------
// 普通鼠标纵向滚轮在隐藏滚动条的胶囊栏上无法触发横向滚动,这里将 deltaY 转置为 scrollLeft。
function attachHorizontalScroll(element) {
  if (!element || element.dataset.horizontalScrollBound === "1") return;
  element.dataset.horizontalScrollBound = "1";
  element.addEventListener(
    "wheel",
    (event) => {
      // 存在纵向滚动且无横向位移时进行转置。
      if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
        event.preventDefault();
        element.scrollLeft += event.deltaY * 0.9;
      }
    },
    { passive: false },
  );
}

// 依据滚动位置切换两端渐变遮罩,直观提示左右仍有未完全展现的收藏夹。
function syncCollectionsOverflow(element) {
  if (!element) return;
  const wrapper = element.closest(".collections-bar-wrapper");
  if (!wrapper) return;
  const maxScroll = element.scrollWidth - element.clientWidth;
  const hasOverflow = maxScroll > 1;
  wrapper.classList.toggle("has-overflow-start", hasOverflow && element.scrollLeft > 1);
  wrapper.classList.toggle("has-overflow-end", hasOverflow && element.scrollLeft < maxScroll - 1);
}

// 新建收藏夹后平滑滚动至最右端,确保新分类胶囊进入视野。
function scrollCollectionsToEnd(element) {
  if (!element) return;
  element.scrollTo({ left: element.scrollWidth, behavior: "smooth" });
  syncCollectionsOverflow(element);
}

function bindCollectionsBar(element) {
  if (!element) return;
  attachHorizontalScroll(element);
  if (element.dataset.overflowBound !== "1") {
    element.dataset.overflowBound = "1";
    element.addEventListener("scroll", () => syncCollectionsOverflow(element), { passive: true });
    if (typeof ResizeObserver === "function") {
      const observer = new ResizeObserver(() => syncCollectionsOverflow(element));
      observer.observe(element);
    }
  }
  syncCollectionsOverflow(element);
}

// ---------- 作品库二级筛选胶囊栏 ----------
async function loadGalleryCollections() {
  const requestId = ++galleryCollectionsRequest;
  try {
    const payload = await request("/api/gallery/collections");
    if (requestId !== galleryCollectionsRequest) return;
    // 新结构为 { all_total, collections };兼容旧版 { items } 返回。
    const collections = Array.isArray(payload?.collections)
      ? payload.collections
      : Array.isArray(payload?.items)
        ? payload.items
        : [];
    galleryCollections = collections;
    const allTotal = Number(payload?.all_total);
    if (Number.isFinite(allTotal)) {
      galleryAllTotal = Math.max(0, allTotal);
    } else {
      // 兼容旧版接口:退化为“全部”视图缓存总数,再退化为各收藏夹计数之和。
      const allData = cachedHistoryPage(1, 0);
      galleryAllTotal = Number.isFinite(Number(allData?.total))
        ? Number(allData.total)
        : galleryCollections.reduce((sum, item) => sum + Number(item.item_count || 0), 0);
    }
    // 当前激活的收藏夹若已被删除,自动回落到“全部作品”。
    if (
      activeCollectionId !== 0 &&
      !galleryCollections.some((item) => Number(item.id) === activeCollectionId)
    ) {
      activeCollectionId = 0;
    }
    renderGalleryCollections();
  } catch (error) {
    if (requestId !== galleryCollectionsRequest) return;
    toast(error.message);
  }
}

function galleryTotalCount() {
  // “全部”徽标只使用后端返回的全库总数,严禁用各收藏夹计数累加(会重复计数且时序不稳)。
  return Math.max(0, Number(galleryAllTotal) || 0);
}

function createCollectionPill({ id, icon, name, count, active, deletable }) {
  const pill = document.createElement("button");
  pill.type = "button";
  pill.className = "collection-pill";
  // “全部”胶囊附加 pill-all 类,便于 renderHistoryPage 就地更新其徽标。
  if (Number(id) === 0) pill.classList.add("pill-all");
  pill.dataset.collectionId = String(id);
  pill.setAttribute("aria-pressed", active ? "true" : "false");
  if (active) pill.classList.add("active");
  const iconSpan = document.createElement("span");
  iconSpan.className = "collection-pill-icon";
  iconSpan.setAttribute("aria-hidden", "true");
  iconSpan.textContent = icon;
  const nameSpan = document.createElement("span");
  nameSpan.className = "collection-pill-name";
  nameSpan.textContent = name;
  const badge = document.createElement("span");
  badge.className = "pill-badge";
  badge.textContent = String(count);
  pill.append(iconSpan, nameSpan, badge);
  pill.addEventListener("click", () => selectGalleryCollection(id));
  if (deletable) {
    // 双击胶囊快速重命名(快捷操作)。
    pill.addEventListener("dblclick", (event) => {
      event.stopPropagation();
      event.preventDefault();
      openCollectionRenameDialog("gallery", id, name);
    });

    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.className = "collection-pill-edit";
    editBtn.title = `重命名“${name}”`;
    editBtn.setAttribute("aria-label", `重命名 ${name}`);
    editBtn.textContent = "✎";
    editBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      event.preventDefault();
      openCollectionRenameDialog("gallery", id, name);
    });
    pill.append(editBtn);

    const menu = document.createElement("button");
    menu.type = "button";
    menu.className = "collection-pill-menu";
    menu.title = `删除收藏夹“${name}”`;
    menu.setAttribute("aria-label", `删除收藏夹 ${name}`);
    menu.textContent = "···";
    menu.addEventListener("click", (event) => {
      event.stopPropagation();
      event.preventDefault();
      openCollectionDeleteDialog("gallery", id, name);
    });
    pill.append(menu);
  }
  return pill;
}

function renderGalleryCollections() {
  if (!ui.galleryCollectionsBar) return;
  const pills = [
    createCollectionPill({
      id: 0,
      icon: "▦",
      name: "全部",
      count: galleryTotalCount(),
      active: activeCollectionId === 0,
      deletable: false,
    }),
  ];
  const ordered = [...galleryCollections].sort((a, b) => {
    const defaultDelta = Number(Boolean(b.is_default)) - Number(Boolean(a.is_default));
    if (defaultDelta) return defaultDelta;
    return Number(a.sort_order || 0) - Number(b.sort_order || 0) || Number(a.id) - Number(b.id);
  });
  for (const collection of ordered) {
    const id = Number(collection.id);
    pills.push(
      createCollectionPill({
        id,
        icon: collection.is_default ? "★" : "📁",
        name: String(collection.name || "未命名"),
        count: Number(collection.item_count || 0),
        active: activeCollectionId === id,
        deletable: !collection.is_default,
      }),
    );
  }
  // 新建入口已改为右侧常驻静态按钮(#btnGalleryAddCollection),不再随胶囊列表滚动。
  ui.galleryCollectionsBar.replaceChildren(...pills);
  syncCollectionsOverflow(ui.galleryCollectionsBar);
}

function selectGalleryCollection(collectionId) {
  const target = Number(collectionId) || 0;
  if (target === activeCollectionId) return;
  activeCollectionId = target;
  renderGalleryCollections();
  loadHistory(1);
}

// ---------- 新建 / 删除收藏夹（分类）状态机 ----------
let collectionCreateContext = null; // { type: 'gallery' | 'preset' }
let collectionDeleteContext = null; // { type: 'gallery' | 'preset', id: number, name: string }
let collectionActionBusy = false;

function setCollectionCreateError(message = "") {
  if (!ui.collectionCreateError) return;
  ui.collectionCreateError.textContent = message;
  ui.collectionCreateError.hidden = !message;
}

function setCollectionDeleteError(message = "") {
  if (!ui.collectionDeleteError) return;
  ui.collectionDeleteError.textContent = message;
  ui.collectionDeleteError.hidden = !message;
}

function openCollectionCreateDialog(type = "gallery") {
  if (!ui.collectionCreateDialog) return;
  const isSub = type === "preset_sub";
  const parentId = isSub ? Number(currentPresetParentId) || 0 : null;
  const parentObj = parentId
    ? presetCollections.find((c) => Number(c.id) === parentId)
    : null;
  collectionCreateContext = { type, parentId };
  const isGallery = type === "gallery";

  if (ui.collectionCreateKicker) {
    ui.collectionCreateKicker.textContent = isSub
      ? "NEW SUB-COLLECTION"
      : isGallery
        ? "GALLERY COLLECTION"
        : "PRESET PARENT COLLECTION";
  }
  if (ui.collectionCreateTitle) {
    ui.collectionCreateTitle.textContent = isSub
      ? `新建子文件夹（归属：${parentObj ? parentObj.name : "当前母类"}）`
      : isGallery
        ? "新建收藏夹"
        : "新建母文件夹";
  }
  if (ui.collectionCreateLabel) {
    ui.collectionCreateLabel.textContent = isGallery ? "收藏夹名称" : isSub ? "子文件夹名称" : "文件夹名称";
  }
  if (ui.collectionCreateInput) {
    ui.collectionCreateInput.maxLength = isGallery ? 40 : 100;
    ui.collectionCreateInput.placeholder = isGallery
      ? "例如：常用精选、待修壁纸"
      : isSub
        ? "例如：站姿特写、双人交互"
        : "例如：姿势库、场景库";
    ui.collectionCreateInput.value = "";
  }
  if (ui.collectionCreateHint) {
    ui.collectionCreateHint.textContent = isGallery ? "最多 40 个字符" : "最多 100 个字符";
  }

  setCollectionCreateError("");
  if (ui.submitCollectionCreate) {
    ui.submitCollectionCreate.disabled = false;
    ui.submitCollectionCreate.textContent = "确认创建";
  }

  ui.collectionCreateDialog.showModal();
  ui.collectionCreateInput?.focus();
}

function closeCollectionCreateDialog() {
  collectionCreateContext = null;
  ui.collectionCreateDialog?.close();
}

function openCollectionDeleteDialog(type, id, name) {
  if (!ui.collectionDeleteDialog) return;
  const targetId = Number(id);
  if (!Number.isFinite(targetId) || targetId <= 0) return;

  collectionDeleteContext = { type, id: targetId, name: String(name || "") };
  const isGallery = type === "gallery";
  const isSub = type === "preset_sub";

  if (ui.collectionDeleteKicker) {
    ui.collectionDeleteKicker.textContent = isGallery
      ? "DELETE GALLERY COLLECTION"
      : isSub
        ? "DELETE PRESET SUB-COLLECTION"
        : "DELETE PRESET PARENT COLLECTION";
  }
  if (ui.collectionDeleteTitle) {
    ui.collectionDeleteTitle.textContent = isGallery
      ? "删除收藏夹"
      : isSub
        ? "删除子文件夹"
        : "删除母文件夹";
  }
  if (ui.collectionDeleteSummary) {
    ui.collectionDeleteSummary.textContent = isGallery
      ? `确定要删除收藏夹“${name}”吗？`
      : isSub
        ? `确定要删除子文件夹“${name}”吗？`
        : `确定要删除母文件夹“${name}”吗？其名下的所有子分类将一并解绑移除。`;
  }
  if (ui.collectionDeleteHint) {
    ui.collectionDeleteHint.textContent = isGallery
      ? "提示：收藏夹删除后，作品本身不会被删除，仅解除收藏夹归属。"
      : "提示：文件夹删除后，预设本体完好保留，仅解除归类归属。";
  }

  setCollectionDeleteError("");
  if (ui.confirmCollectionDelete) {
    ui.confirmCollectionDelete.disabled = false;
    ui.confirmCollectionDelete.textContent = "确认删除";
  }

  ui.collectionDeleteDialog.showModal();
}

function closeCollectionDeleteDialog() {
  collectionDeleteContext = null;
  ui.collectionDeleteDialog?.close();
}

// 重构：创建表单提交（替代原生 window.prompt）
async function submitCollectionCreate(event) {
  event?.preventDefault();
  const context = collectionCreateContext;
  if (!context || collectionActionBusy || !ui.submitCollectionCreate) return;

  const input = ui.collectionCreateInput;
  const raw = (input?.value || "").trim();
  const isGallery = context.type === "gallery";
  const isSub = context.type === "preset_sub";

  if (!raw) {
    setCollectionCreateError(isGallery ? "收藏夹名称不能为空" : "分类名称不能为空");
    input?.focus();
    return;
  }

  // 客户端同名预检:子文件夹只在同一母类下比对,母文件夹只在顶级比对。
  const isDuplicate = isGallery
    ? galleryCollections.some((c) => (c.name || "").trim().toLowerCase() === raw.toLowerCase())
    : isSub
      ? presetSubCollections(context.parentId).some(
          (c) => (c.name || "").trim().toLowerCase() === raw.toLowerCase(),
        )
      : presetParentCollections().some(
          (c) => (c.name || "").trim().toLowerCase() === raw.toLowerCase(),
        );

  if (isDuplicate) {
    setCollectionCreateError(isGallery ? "已有同名收藏夹" : "已有同名分类");
    input?.focus();
    return;
  }

  collectionActionBusy = true;
  ui.submitCollectionCreate.disabled = true;
  ui.submitCollectionCreate.textContent = "正在创建...";
  setCollectionCreateError("");

  try {
    if (isGallery) {
      const created = await request("/api/gallery/collections", {
        method: "POST",
        body: JSON.stringify({ name: raw }),
      });
      await loadGalleryCollections();
      // 创建成功后自动切换到新收藏夹视图。
      activeCollectionId = Number(created?.id) || 0;
      renderGalleryCollections();
      scrollCollectionsToEnd(ui.galleryCollectionsBar);
      loadHistory(1);
      toast(`已创建收藏夹“${raw}”`);
    } else if (isSub) {
      // 提交到后端创建子分类。
      const created = await request("/api/style-presets/collections", {
        method: "POST",
        body: JSON.stringify({ name: raw, parent_id: context.parentId }),
      });
      await loadPresetCollections();
      // 创建成功后自动激活新创建的子分类并滚动到末尾。
      currentPresetSubId = Number(created?.id) || 0;
      presetPage = 1;
      renderPresetCollections();
      renderPresetSubCollections();
      scrollCollectionsToEnd(ui.presetSubCollectionsBar);
      renderStylePresets();
      toast(`已在当前母分类下创建子文件夹“${raw}”`);
    } else {
      // 创建母文件夹:显式传 parent_id=null,避免后端误判为子分类。
      const created = await request("/api/style-presets/collections", {
        method: "POST",
        body: JSON.stringify({ name: raw, parent_id: null }),
      });
      await loadPresetCollections();
      // 创建成功后自动切换到新分类视图。
      currentPresetParentId = Number(created?.id) || 0;
      currentPresetSubId = 0;
      presetPage = 1;
      renderPresetCollections();
      renderPresetSubCollections();
      scrollCollectionsToEnd(ui.presetCollectionsBar);
      renderStylePresets();
      toast(`已创建分类“${raw}”`);
    }
    closeCollectionCreateDialog();
  } catch (error) {
    setCollectionCreateError(error.message || "创建失败，请重试");
  } finally {
    collectionActionBusy = false;
    if (ui.submitCollectionCreate) {
      ui.submitCollectionCreate.disabled = false;
      ui.submitCollectionCreate.textContent = "确认创建";
    }
  }
}

// 重构：删除确认提交（替代原生 window.confirm）
async function submitCollectionDelete(event) {
  event?.preventDefault();
  const context = collectionDeleteContext;
  if (!context || collectionActionBusy || !ui.confirmCollectionDelete) return;

  const { type, id, name } = context;
  const isGallery = type === "gallery";

  collectionActionBusy = true;
  ui.confirmCollectionDelete.disabled = true;
  ui.confirmCollectionDelete.textContent = "正在删除...";
  setCollectionDeleteError("");

  try {
    if (isGallery) {
      await request(`/api/gallery/collections/${id}`, { method: "DELETE" });
      if (activeCollectionId === id) activeCollectionId = 0;
      await loadGalleryCollections();
      loadHistory(1);
      toast(`已删除收藏夹“${name}”`);
    } else {
      await request(`/api/style-presets/collections/${id}`, { method: "DELETE" });
      // 本地同步解绑,避免等待全量刷新期间徽标与卡片归属不一致。
      for (const item of stylePresets) {
        const ids = presetCollectionIds(item);
        if (ids.includes(id)) {
          item.collection_ids = ids.filter((val) => val !== id);
          item.favorite = item.collection_ids.includes(DEFAULT_COLLECTION_ID);
        }
      }
      if (type === "preset_sub") {
        // 若删除的是当前激活的子分类,回退至该母分类下的第一个子分类。
        if (Number(currentPresetSubId) === id) {
          const remaining = presetSubCollections(currentPresetParentId);
          currentPresetSubId = remaining.length > 0 ? Number(remaining[0].id) : 0;
        }
      } else if (Number(currentPresetParentId) === id) {
        // 若删除的是当前激活的母分类,回退到全部。
        currentPresetParentId = 0;
        currentPresetSubId = 0;
      }
      presetPage = 1;
      await loadPresetCollections();
      renderPresetCollections();
      renderPresetSubCollections();
      renderStylePresets();
      toast(`已删除分类“${name}”`);
    }
    closeCollectionDeleteDialog();
  } catch (error) {
    setCollectionDeleteError(error.message || "删除失败，请重试");
  } finally {
    collectionActionBusy = false;
    if (ui.confirmCollectionDelete) {
      ui.confirmCollectionDelete.disabled = false;
      ui.confirmCollectionDelete.textContent = "确认删除";
    }
  }
}

// ---------- 重命名收藏夹 / 分类状态机 ----------
let collectionRenameContext = null; // { type: 'gallery' | 'preset', id: number, name: string }

function setCollectionRenameError(message = "") {
  if (!ui.collectionRenameError) return;
  ui.collectionRenameError.textContent = message;
  ui.collectionRenameError.hidden = !message;
}

function openCollectionRenameDialog(type, id, currentName) {
  if (!ui.collectionRenameDialog) return;
  const targetId = Number(id);
  if (!Number.isFinite(targetId) || targetId <= 0) return;

  collectionRenameContext = { type, id: targetId, name: String(currentName || "") };
  const isGallery = type === "gallery";
  const isSub = type === "preset_sub";

  if (ui.collectionRenameKicker) {
    ui.collectionRenameKicker.textContent = isGallery
      ? "RENAME GALLERY COLLECTION"
      : isSub
        ? "RENAME PRESET SUB-COLLECTION"
        : "RENAME PRESET PARENT COLLECTION";
  }
  if (ui.collectionRenameTitle) {
    ui.collectionRenameTitle.textContent = isGallery
      ? "重命名收藏夹"
      : isSub
        ? "重命名子文件夹"
        : "重命名母文件夹";
  }
  if (ui.collectionRenameLabel) {
    ui.collectionRenameLabel.textContent = isGallery ? "收藏夹名称" : isSub ? "子文件夹名称" : "文件夹名称";
  }
  if (ui.collectionRenameInput) {
    ui.collectionRenameInput.maxLength = isGallery ? 40 : 100;
    ui.collectionRenameInput.value = currentName || "";
  }
  if (ui.collectionRenameHint) {
    ui.collectionRenameHint.textContent = isGallery ? "最多 40 个字符" : "最多 100 个字符";
  }

  setCollectionRenameError("");
  if (ui.submitCollectionRename) {
    ui.submitCollectionRename.disabled = false;
    ui.submitCollectionRename.textContent = "保存修改";
  }

  ui.collectionRenameDialog.showModal();
  ui.collectionRenameInput?.focus();
  ui.collectionRenameInput?.select();
}

function closeCollectionRenameDialog() {
  collectionRenameContext = null;
  ui.collectionRenameDialog?.close();
}

async function submitCollectionRename(event) {
  event?.preventDefault();
  const context = collectionRenameContext;
  if (!context || collectionActionBusy || !ui.submitCollectionRename) return;

  const input = ui.collectionRenameInput;
  const raw = (input?.value || "").trim();
  const isGallery = context.type === "gallery";
  const isSub = context.type === "preset_sub";

  if (!raw) {
    setCollectionRenameError(isGallery ? "收藏夹名称不能为空" : "分类名称不能为空");
    input?.focus();
    return;
  }

  // 无实质修改:直接关闭,省去网络请求。
  if (raw === context.name) {
    closeCollectionRenameDialog();
    return;
  }

  // 客户端同名预检(大小写不敏感,排除自身);子文件夹只在同一母类下比对。
  const renameScope = isSub
    ? presetCollections.filter(
        (c) => Number(c.parent_id) === Number(currentPresetParentId),
      )
    : presetCollections;
  const isDuplicate = isGallery
    ? galleryCollections.some(
        (c) => Number(c.id) !== context.id && (c.name || "").trim().toLowerCase() === raw.toLowerCase(),
      )
    : renameScope.some(
        (c) => Number(c.id) !== context.id && (c.name || "").trim().toLowerCase() === raw.toLowerCase(),
      );

  if (isDuplicate) {
    setCollectionRenameError(isGallery ? "已有同名收藏夹" : "已有同名分类");
    input?.focus();
    return;
  }

  collectionActionBusy = true;
  ui.submitCollectionRename.disabled = true;
  ui.submitCollectionRename.textContent = "正在保存...";
  setCollectionRenameError("");

  try {
    if (isGallery) {
      const updated = await request(`/api/gallery/collections/${context.id}`, {
        method: "PATCH",
        body: JSON.stringify({ name: raw }),
      });
      // 就地更新本地缓存,保持 activeCollectionId 与分页不变。
      const item = galleryCollections.find((c) => Number(c.id) === context.id);
      if (item) item.name = updated?.name || raw;
      renderGalleryCollections();
      toast(`收藏夹已重命名为“${raw}”`);
    } else {
      const updated = await request(`/api/style-presets/collections/${context.id}`, {
        method: "PATCH",
        body: JSON.stringify({ name: raw }),
      });
      const item = presetCollections.find((c) => Number(c.id) === context.id);
      if (item) item.name = updated?.name || raw;
      renderPresetCollections();
      renderPresetSubCollections();
      toast(`${isSub ? "子文件夹" : "分类"}已重命名为“${raw}”`);
    }
    closeCollectionRenameDialog();
  } catch (error) {
    setCollectionRenameError(error.message || "修改失败，请重试");
  } finally {
    collectionActionBusy = false;
    if (ui.submitCollectionRename) {
      ui.submitCollectionRename.disabled = false;
      ui.submitCollectionRename.textContent = "保存修改";
    }
  }
}

// ---------- 详情页“收藏至...”多选弹窗 ----------
function setImageCollectionsError(message = "") {
  if (!ui.imageCollectionsError) return;
  ui.imageCollectionsError.textContent = message;
  ui.imageCollectionsError.hidden = !message;
}

function renderImageCollectionsChecklist(checkedIds = []) {
  if (!ui.imageCollectionsChecklist) return;
  const checked = new Set(checkedIds.map(Number));
  const ordered = [...galleryCollections].sort((a, b) => {
    const defaultDelta = Number(Boolean(b.is_default)) - Number(Boolean(a.is_default));
    if (defaultDelta) return defaultDelta;
    return Number(a.sort_order || 0) - Number(b.sort_order || 0) || Number(a.id) - Number(b.id);
  });
  const rows = ordered.map((collection) => {
    const id = Number(collection.id);
    const label = document.createElement("label");
    label.className = "favorite-group-check";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = String(id);
    input.checked = checked.has(id);
    const text = document.createElement("span");
    text.textContent = `${collection.is_default ? "★ " : ""}${collection.name || "未命名"}`;
    const count = document.createElement("small");
    count.textContent = `${Number(collection.item_count || 0)} 张`;
    count.style.marginLeft = "auto";
    count.style.color = "var(--text-tertiary)";
    label.append(input, text, count);
    return label;
  });
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.className = "import-hint";
    empty.textContent = "暂无可用收藏夹，请先在下方新建。";
    rows.push(empty);
  }
  ui.imageCollectionsChecklist.replaceChildren(...rows);
}

function openImageCollectionsDialog() {
  if (!selectedRecord) return;
  // 单图模式进入前复位批量态,防止上次批量操作残留的警告与危险按钮样式。
  resetBatchCollectionsState();
  setImageCollectionsError("");
  if (ui.newCollectionNameInput) ui.newCollectionNameInput.value = "";
  const ids = Array.isArray(selectedRecord.collection_ids) ? selectedRecord.collection_ids : [];
  renderImageCollectionsChecklist(ids);
  ui.imageCollectionsDialog.showModal();
}

function checkedImageCollectionIds() {
  if (!ui.imageCollectionsChecklist) return [];
  return [...ui.imageCollectionsChecklist.querySelectorAll('input[type="checkbox"]:checked')]
    .map((input) => Number(input.value))
    .filter((value) => Number.isFinite(value) && value > 0);
}

async function createAndCheckCollection() {
  const input = ui.newCollectionNameInput;
  const name = (input?.value || "").trim();
  if (!name) {
    setImageCollectionsError("请输入收藏夹名称");
    input?.focus();
    return;
  }
  if (ui.btnCreateAndCheckCollection) ui.btnCreateAndCheckCollection.disabled = true;
  try {
    const created = await request("/api/gallery/collections", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    await loadGalleryCollections();
    const checked = checkedImageCollectionIds();
    const createdId = Number(created?.id);
    if (Number.isFinite(createdId) && !checked.includes(createdId)) checked.push(createdId);
    renderImageCollectionsChecklist(checked);
    if (input) input.value = "";
    setImageCollectionsError("");
    // 批量收藏弹窗中新建收藏夹:保留批量上下文与提示文案,不切回单图模式。
    if (batchFavoriteContext) {
      const hint = ui.imageCollectionsDialog?.querySelector(".import-hint");
      if (hint) {
        hint.textContent = `已选 ${batchFavoriteContext.ids.length} 张作品，勾选要归入的收藏夹（保存后将覆盖这些作品的收藏归属）：`;
      }
      // 新建项默认勾选,需同步刷新警告与保存按钮状态。
      updateBatchCollectionsState();
    }
  } catch (error) {
    setImageCollectionsError(error.message);
  } finally {
    if (ui.btnCreateAndCheckCollection) ui.btnCreateAndCheckCollection.disabled = false;
  }
}

async function saveImageCollections() {
  const record = selectedRecord;
  if (!record || imageCollectionsSaving) return;
  const collectionIds = checkedImageCollectionIds();
  imageCollectionsSaving = true;
  if (ui.saveImageCollections) ui.saveImageCollections.disabled = true;
  setImageCollectionsError("");
  try {
    const result = await request(`/api/history/${record.id}/collections`, {
      method: "POST",
      body: JSON.stringify({ collection_ids: collectionIds }),
    });
    const updated = Array.isArray(result?.collection_ids) ? result.collection_ids : collectionIds;
    syncCachedCollections(record.id, updated);
    // 卡片星标与详情页状态双向联动。
    paintCardFavorite(record.id, isDefaultFavorite(record));
    ui.imageCollectionsDialog.close();
    await loadGalleryCollections();
    toast("已更新收藏归属");
  } catch (error) {
    setImageCollectionsError(error.message);
  } finally {
    imageCollectionsSaving = false;
    if (ui.saveImageCollections) ui.saveImageCollections.disabled = false;
  }
}

function renderDetail(record) {
  const settings = normalizeSettings(record.settings || {});
  ui.detailImage.src = `/api/images/${record.id}`;
  ui.detailImage.alt = record.filename ? `生成结果：${record.filename}` : "生成结果";
  ui.detailMeta.textContent = `${record.created_at || ""} · ${record.filename || ""}`;
  ui.detailPositive.value = record.positive_prompt || record.resolved_prompt || "";
  ui.detailNegative.value = record.negative_prompt || "";
  const stats = [
    ["尺寸", `${settings.width} × ${settings.height}`],
    ["采样", `${settings.sampler_name} / ${settings.scheduler} / ${settings.steps} steps / CFG ${settings.cfg}`],
    ["图像种子", record.sample_seed],
    ["提示词种子", record.prompt_seed],
    ["人物", `${settings.female_count || 0} 女 / ${settings.male_count || 0} 男`],
  ];
  ui.detailStats.innerHTML = stats
    .map(([key, value]) => `<div><dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd></div>`)
    .join("");
  const selected = record.resolved_selection || {};
  const activeLoras = (settings.loras || []).filter((item) => item.enabled);
  const loraText = activeLoras.length
    ? activeLoras.map((item) => `${escapeHtml(item.filename)} × ${escapeHtml(item.strength)}`).join("、")
    : "未使用";
  ui.detailSelection.innerHTML = `<span class="kicker">ACTUAL DRAW</span><div>${SECTIONS.map((section) => `<span><b>${SECTION_META[section].label}</b>${(selected[section] || []).map((item) => escapeHtml(item.title)).join("、") || "未使用"}</span>`).join("")}<span><b>LoRA</b>${loraText}</span></div>`;
}

function openDetail(record) {
  closeImagePreview({ immediate: true, restoreFocus: false });
  selectedRecord = record;
  regenerationOptions = null;
  closeRegenerationDrawers(false);
  renderDetail(record);
  updatePreviewNavigation();
  updateDetailNavigation();
  ui.detailDialog.showModal();
}

let detailNavInFlight = false;

// 状态更新：仅依据 selectedRecord 与相邻索引计算，绝不读取 imagePreview.phase
function updateDetailNavigation() {
  if (!selectedRecord) {
    if (ui.detailPrevious) ui.detailPrevious.disabled = true;
    if (ui.detailNext) ui.detailNext.disabled = true;
    return;
  }
  const prevAvailable = previewNeighborAvailable(-1);
  const nextAvailable = previewNeighborAvailable(1);
  if (ui.detailPrevious) ui.detailPrevious.disabled = !prevAvailable;
  if (ui.detailNext) ui.detailNext.disabled = !nextAvailable;
}

async function navigateDetail(direction) {
  if (!ui.detailDialog.open || !selectedRecord || detailNavInFlight) return;
  // 全屏原图预览打开时，方向键由全屏模块接管，此处忽略
  if (imagePreview.phase !== "closed") return;

  const location = selectedHistoryLocation();
  let target = previewNeighbor(direction, location);
  if (!target) return;

  detailNavInFlight = true;
  updateDetailNavigation();

  try {
    // 跨页处理：相邻图片若在未载入的上一页或下一页，发起异步获取
    if (!target.record) {
      if (ui.detailNavStatus) ui.detailNavStatus.textContent = "正在加载相邻作品…";
      target.data = await loadHistoryPageForPreview(target.page);
      const items = Array.isArray(target.data.items) ? target.data.items : [];
      target.record = items[direction > 0 ? 0 : items.length - 1];
      if (target.record && target.data) {
        // 同步刷新底层画廊，保证翻页状态与页码一致
        renderHistoryPage(target.data);
      }
    }

    if (!target.record) return;

    // 切图时重置当前可能展开的抽屉（避免上张图的变体/种子数据残留）
    closeRegenerationDrawers(false);
    regenerationOptions = null;

    // 切换当前选中项并重新渲染详情面板
    selectedRecord = target.record;
    renderDetail(target.record);

    if (ui.detailNavStatus) {
      ui.detailNavStatus.textContent = `已切至 ${previewPositionLabel(target.record)}`;
    }

    // 后台静默预加载相邻原图缓存
    preloadPreviewNeighbors();
  } catch (error) {
    toast(error.message || "切换作品失败");
  } finally {
    detailNavInFlight = false;
    updateDetailNavigation();
  }
}

const IMAGE_PREVIEW_MAX_ZOOM = 4;
const imagePreviewReducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const clampPreview = (value, min, max) => Math.min(max, Math.max(min, value));
const previewMotion = (name, fallback) => {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const duration = Number.parseFloat(value);
  return Number.isFinite(duration) ? duration : fallback;
};

function previewRecordIndex(record, items = historyItems) {
  if (!record || !Array.isArray(items)) return -1;
  return items.findIndex((item) => String(item.id) === String(record.id));
}

function selectedHistoryLocation() {
  const currentIndex = previewRecordIndex(selectedRecord);
  if (currentIndex >= 0) return { page: historyPage, items: historyItems, index: currentIndex };
  // 仅在当前收藏夹视图的缓存中查找,避免跨视图串页。
  for (const [key, data] of historyCache) {
    if (!String(key).startsWith(`${activeCollectionId}_`)) continue;
    const items = Array.isArray(data?.items) ? data.items : [];
    const index = previewRecordIndex(selectedRecord, items);
    if (index >= 0) return { page: Number(data.page) || 1, items, index };
  }
  return { page: historyPage, items: historyItems, index: -1 };
}

function previewNeighborAvailable(direction) {
  const location = selectedHistoryLocation();
  if (location.index >= 0 && location.index + direction >= 0 && location.index + direction < location.items.length) return true;
  const targetPage = location.page + (direction > 0 ? 1 : -1);
  return targetPage >= 1 && targetPage <= historyPages;
}

function updatePreviewNavigation() {
  const active = Boolean(selectedRecord && imagePreview.phase !== "closed");
  const locked = ["loading", "switching", "closing"].includes(imagePreview.phase);
  const previousAvailable = active && previewNeighborAvailable(-1);
  const nextAvailable = active && previewNeighborAvailable(1);
  ui.imagePreviewPrevious.disabled = locked || !previousAvailable;
  ui.imagePreviewNext.disabled = locked || !nextAvailable;
  ui.imagePreviewDialog.classList.toggle("has-navigation", active && (previousAvailable || nextAvailable));
}

function announcePreview(message) {
  ui.imagePreviewAnnouncement.textContent = message;
}

function previewPositionLabel(record = selectedRecord) {
  const location = previewRecordIndex(record) >= 0
    ? { page: historyPage, items: historyItems, index: previewRecordIndex(record) }
    : selectedHistoryLocation();
  if (location.index < 0) return record?.filename || "当前图片";
  const total = Number(ui.historyCount.textContent.match(/\d+/)?.[0] || 0);
  let position = (location.page - 1) * 24 + location.index + 1;
  let priorPagesAreCached = true;
  let cachedBefore = 0;
  for (let page = 1; page < location.page; page += 1) {
    const data = cachedHistoryPage(page);
    if (!data || !Array.isArray(data.items)) {
      priorPagesAreCached = false;
      break;
    }
    cachedBefore += data.items.length;
  }
  if (priorPagesAreCached) position = cachedBefore + location.index + 1;
  return `${record?.filename || "当前图片"}，第 ${position} 张${total ? `，共 ${total} 张` : ""}`;
}

function preloadRecord(record) {
  if (!record) return Promise.resolve(null);
  const key = String(record.id);
  const cached = imagePreview.preloaded.get(key);
  if (cached) return cached;
  const image = new Image();
  image.decoding = "async";
  image.src = `/api/images/${record.id}`;
  const promise = image.decode()
    .then(() => image)
    .catch(() => {
      imagePreview.preloaded.delete(key);
      return null;
    });
  imagePreview.preloaded.set(key, promise);
  return promise;
}

function preloadPreviewNeighbors() {
  const location = selectedHistoryLocation();
  if (location.index < 0) return;
  for (const direction of [-1, 1]) {
    const neighbor = location.items[location.index + direction];
    if (neighbor) preloadRecord(neighbor);
  }
}

async function loadHistoryPageForPreview(page) {
  const cached = cachedHistoryPage(page);
  if (cached) return cached;
  const data = await request(
    `/api/history?page=${page}&limit=24&collection_id=${activeCollectionId}`,
  );
  cacheHistoryPage(data);
  return data;
}

function previewNeighbor(direction, location = selectedHistoryLocation()) {
  const index = location.index + direction;
  if (location.index >= 0 && index >= 0 && index < location.items.length) {
    return { record: location.items[index], page: location.page, data: null };
  }
  const targetPage = location.page + (direction > 0 ? 1 : -1);
  if (targetPage < 1 || targetPage > historyPages) return null;
  return { record: null, page: targetPage, data: null };
}

function playPreviewAnimation(from, to, duration) {
  cancelImagePreviewAnimation();
  const reduce = imagePreviewReducedMotion();
  const animation = ui.imagePreviewImage.animate(
    reduce ? [from, to] : [from, to],
    { duration: reduce ? 120 : duration, easing: getComputedStyle(document.documentElement).getPropertyValue("--spring").trim(), fill: "both" },
  );
  imagePreview.animation = animation;
  return animation.finished.then(() => {
    if (imagePreview.animation === animation) {
      animation.commitStyles();
      animation.cancel();
      imagePreview.animation = null;
    }
    return true;
  }).catch(() => false);
}

async function switchPreviewImage(record, requestId) {
  const previousRecord = selectedRecord;
  const previousSrc = ui.imagePreviewImage.currentSrc || ui.imagePreviewImage.src;
  const image = await preloadRecord(record);
  if (!image || requestId !== imagePreview.navigationRequest || imagePreview.phase !== "switching") return false;
  const fadeOut = await playPreviewAnimation(liveImagePreviewFrame(), { ...liveImagePreviewFrame(), opacity: 0 }, previewMotion("--motion-fast", 150));
  if (!fadeOut || requestId !== imagePreview.navigationRequest || imagePreview.phase !== "switching") return false;

  selectedRecord = record;
  renderDetail(record);
  ui.imagePreviewImage.src = `/api/images/${record.id}`;
  ui.imagePreviewImage.alt = `生成结果全尺寸预览：${record.filename || "当前图片"}`;
  ui.imagePreviewImage.hidden = false;
  ui.imagePreviewImage.style.opacity = "0";
  imagePreview.zoom = 1;
  imagePreview.x = imagePreview.y = 0;
  let decoded = true;
  try {
    await ui.imagePreviewImage.decode();
  } catch {
    decoded = false;
  }
  if (!decoded && requestId === imagePreview.navigationRequest && imagePreview.phase === "switching") {
    selectedRecord = previousRecord;
    renderDetail(previousRecord);
    ui.imagePreviewImage.src = previousSrc;
    ui.imagePreviewImage.alt = `生成结果全尺寸预览：${previousRecord?.filename || "当前图片"}`;
    ui.imagePreviewImage.hidden = false;
    ui.imagePreviewImage.style.opacity = "1";
    imagePreview.zoom = 1;
    imagePreview.x = imagePreview.y = 0;
    await ui.imagePreviewImage.decode().catch(() => null);
    layoutImagePreview();
    ui.imagePreviewTitle.textContent = previousRecord?.filename || "全尺寸图片预览";
  }
  if (requestId !== imagePreview.navigationRequest || imagePreview.phase !== "switching") return false;
  layoutImagePreview();
  const target = imagePreviewFrame();
  const enter = { ...target, opacity: 0, transform: `${target.transform} scale(.985)` };
  imagePreview.phase = "opening";
  await playPreviewAnimation(enter, target, previewMotion("--motion-medium", 240));
  if (requestId !== imagePreview.navigationRequest) return false;
  imagePreview.phase = "open";
  ui.imagePreviewTitle.textContent = record.filename || "全尺寸图片预览";
  announcePreview(previewPositionLabel(record));
  updatePreviewNavigation();
  ui.imagePreviewDialog.classList.remove("is-navigating");
  preloadPreviewNeighbors();
  return true;
}

async function navigatePreview(direction, focusTarget = null) {
  const restoreFocus = () => {
    if (!focusTarget?.isConnected) return;
    if (!focusTarget.disabled) focusTarget.focus({ preventScroll: true });
    else ui.imagePreviewImage.focus({ preventScroll: true });
  };
  if (imagePreview.phase !== "open") return;
  const requestId = ++imagePreview.navigationRequest;
  ui.imagePreviewDialog.classList.add("is-navigating");
  const location = selectedHistoryLocation();
  let target = previewNeighbor(direction, location);
  if (!target) {
    announcePreview(direction < 0 ? "已经是第一张图片" : "已经是最后一张图片");
    ui.imagePreviewDialog.classList.remove("is-navigating");
    updatePreviewNavigation();
    restoreFocus();
    return;
  }
  if (!target.record) {
    imagePreview.phase = "switching";
    announcePreview("正在加载相邻图片…");
    try {
      target.data = await loadHistoryPageForPreview(target.page);
      const items = Array.isArray(target.data.items) ? target.data.items : [];
      target.record = items[direction > 0 ? 0 : items.length - 1];
    } catch (error) {
      imagePreview.phase = "open";
      ui.imagePreviewDialog.classList.remove("is-navigating");
      updatePreviewNavigation();
      announcePreview(error.message || "相邻图片加载失败");
      restoreFocus();
      return;
    }
    if (!target.record || requestId !== imagePreview.navigationRequest) {
      if (requestId === imagePreview.navigationRequest) {
        imagePreview.phase = "open";
        ui.imagePreviewDialog.classList.remove("is-navigating");
        updatePreviewNavigation();
        restoreFocus();
      }
      return;
    }
    cacheHistoryPage(target.data);
  } else {
    imagePreview.phase = "switching";
  }
  updatePreviewNavigation();
  const switched = await switchPreviewImage(target.record, requestId);
  if (switched && target.data) renderHistoryPage(target.data);
  if (switched) restoreFocus();
  if (!switched && requestId === imagePreview.navigationRequest && imagePreview.phase === "switching") {
    imagePreview.phase = "open";
    ui.imagePreviewDialog.classList.remove("is-navigating");
    announcePreview("图片加载失败，请重试");
    updatePreviewNavigation();
    restoreFocus();
  }
}

function imagePreviewFrame() {
  return { transform: ui.imagePreviewImage.style.transform || "none", clipPath: "inset(0px round 18px)", opacity: 1 };
}

function cancelImagePreviewAnimation() {
  imagePreview.animation?.cancel();
  imagePreview.animation = null;
}

function animateImagePreview(from, to, duration, onFinish = () => {}) {
  cancelImagePreviewAnimation();
  const reduce = imagePreviewReducedMotion();
  const animation = ui.imagePreviewImage.animate(
    reduce ? (imagePreview.phase === "closing" ? [from, { ...from, opacity: 0 }] : [{ ...to, opacity: 0 }, to]) : [from, to],
    { duration: reduce ? 120 : duration, easing: getComputedStyle(document.documentElement).getPropertyValue("--spring").trim(), fill: "both" },
  );
  imagePreview.animation = animation;
  animation.finished.then(() => {
    if (imagePreview.animation !== animation) return;
    cancelImagePreviewAnimation();
    onFinish();
  }).catch(() => {}); // Reversing/closing during an animation is expected.
}

// Fade the veil from its live opacity so interrupting a fade never jumps.
function animateImagePreviewVeil(toOpacity, duration, onFinish = () => {}) {
  const veil = ui.imagePreviewVeil;
  const from = getComputedStyle(veil).opacity;
  veil.getAnimations().forEach(animation => animation.cancel());
  const animation = veil.animate([{ opacity: from }, { opacity: toOpacity }], {
    duration: imagePreviewReducedMotion() ? 120 : duration, fill: "both",
  });
  animation.finished.then(onFinish).catch(() => {});
  return animation;
}

function liveImagePreviewFrame() {
  const style = getComputedStyle(ui.imagePreviewImage);
  return { transform: style.transform, clipPath: style.clipPath, opacity: style.opacity };
}

function clampImagePreviewOffset() {
  const maxX = Math.max(0, (imagePreview.width * imagePreview.zoom - ui.imagePreviewStage.clientWidth) / 2);
  const maxY = Math.max(0, (imagePreview.height * imagePreview.zoom - ui.imagePreviewStage.clientHeight) / 2);
  imagePreview.x = clampPreview(imagePreview.x, -maxX, maxX);
  imagePreview.y = clampPreview(imagePreview.y, -maxY, maxY);
}

function applyImagePreviewTransform() {
  clampImagePreviewOffset();
  ui.imagePreviewImage.style.transform = "translate3d(" + imagePreview.x + "px, " + imagePreview.y + "px, 0) scale(" + imagePreview.zoom + ")";
  ui.imagePreviewImage.classList.toggle("is-zoomed", imagePreview.zoom > 1);
}

function layoutImagePreview() {
  const image = ui.imagePreviewImage;
  const stage = ui.imagePreviewStage;
  const style = getComputedStyle(stage);
  const availableWidth = Math.min(stage.clientWidth * .92, stage.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight));
  const availableHeight = Math.min(stage.clientHeight * .92, stage.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom));
  const fit = Math.min(1, availableWidth / image.naturalWidth, availableHeight / image.naturalHeight);
  imagePreview.width = image.naturalWidth * fit;
  imagePreview.height = image.naturalHeight * fit;
  image.style.width = imagePreview.width + "px";
  image.style.height = imagePreview.height + "px";
  applyImagePreviewTransform();
}

// Reproduce object-fit:cover without stretching; reveal the cropped edges as it opens.
function imagePreviewSourceFrame() {
  const source = ui.detailImage.getBoundingClientRect();
  const dialog = ui.detailDialog.getBoundingClientRect();
  const stage = ui.imagePreviewStage.getBoundingClientRect();
  const scale = Math.max(source.width / imagePreview.width, source.height / imagePreview.height);
  const left = Math.max(source.left, dialog.left + 1, stage.left);
  const top = Math.max(source.top, dialog.top + 1, stage.top);
  const right = Math.min(source.right, dialog.right - 1, stage.right);
  const bottom = Math.min(source.bottom, dialog.bottom - 1, stage.bottom);
  if (!scale || right <= left || bottom <= top) return { ...imagePreviewFrame(), opacity: 0 };
  const cx = source.left + source.width / 2;
  const cy = source.top + source.height / 2;
  const imageLeft = cx - imagePreview.width * scale / 2;
  const imageTop = cy - imagePreview.height * scale / 2;
  const insets = [
    (top - imageTop) / scale,
    (imageLeft + imagePreview.width * scale - right) / scale,
    (imageTop + imagePreview.height * scale - bottom) / scale,
    (left - imageLeft) / scale,
  ].map(value => Math.max(0, value) + "px").join(" ");
  return {
    transform: "translate3d(" + (cx - stage.left - stage.width / 2) + "px, " + (cy - stage.top - stage.height / 2) + "px, 0) scale(" + scale + ")",
    clipPath: "inset(" + insets + " round " + (18 / scale) + "px)",
    opacity: 1,
  };
}

async function openImagePreview(event) {
  event?.stopPropagation(); // Preserve any expanded replay/variant controls underneath.
  if (!selectedRecord || !ui.detailImage.getAttribute("src")) return;

  // Reverse-reopen: if the exit animation is still in flight, bounce back from
  // the live frame instead of ignoring the click (previously felt like a hang).
  if (imagePreview.phase === "closing") {
    ++imagePreview.token; // Cancel the pending finishImagePreviewClose callback.
    if (!ui.imagePreviewDialog.open) {
      // The dialog got closed before we could intercept; restart cleanly.
      imagePreview.phase = "closed";
      return openImagePreview(event);
    }
    imagePreview.phase = "opening";
    const from = liveImagePreviewFrame();
    imagePreview.zoom = 1;
    imagePreview.x = imagePreview.y = 0;
    applyImagePreviewTransform();
    animateImagePreviewVeil(1, previewMotion("--motion-medium", 240));
    animateImagePreview(from, imagePreviewFrame(), previewMotion("--motion-medium", 240), () => {
      if (imagePreview.phase === "opening") imagePreview.phase = "open";
    });
    return;
  }
  if (imagePreview.phase !== "closed") return;

  const token = ++imagePreview.token;
  imagePreview.phase = "loading";
  imagePreview.zoom = 1;
  imagePreview.x = imagePreview.y = 0;
  imagePreview.tap = null;
  // Keep the decoded bitmap between openings. Clearing src here forced a
  // multi-megabyte refetch and decode on every click after the first close.
  ui.imagePreviewImage.hidden = true;
  ui.imagePreviewStatus.hidden = false;
  ui.imagePreviewStatus.textContent = "正在加载原图…";
  ui.imagePreviewImage.src = ui.detailImage.currentSrc || ui.detailImage.src;
  ui.imagePreviewImage.alt = `生成结果全尺寸预览：${selectedRecord.filename || "当前图片"}`;
  ui.imagePreviewTitle.textContent = selectedRecord.filename || "全尺寸图片预览";
  document.documentElement.classList.add("image-preview-open");
  ui.imagePreviewDialog.showModal();
  ui.detailImage.setAttribute("aria-expanded", "true");
  ui.closeImagePreview.focus({ preventScroll: true });
  updatePreviewNavigation();
  announcePreview(`正在打开${previewPositionLabel(selectedRecord)}`);
  animateImagePreviewVeil(1, previewMotion("--motion-slow", 360));
  try {
    await ui.imagePreviewImage.decode();
    if (token !== imagePreview.token || !ui.detailDialog.open) return;
    // If a close was requested while decoding, keep the image hidden and let
    // the in-flight close animation finish instead of starting a new entry.
    if (imagePreview.phase === "closing") return;
    ui.imagePreviewStatus.hidden = true;
    ui.imagePreviewImage.hidden = false;
    layoutImagePreview();
    imagePreview.phase = "opening";
    animateImagePreview(imagePreviewSourceFrame(), imagePreviewFrame(), previewMotion("--motion-slow", 360), () => {
      if (imagePreview.phase === "opening") {
        imagePreview.phase = "open";
        updatePreviewNavigation();
        announcePreview(previewPositionLabel(selectedRecord));
        preloadPreviewNeighbors();
      }
    });
  } catch {
    if (token !== imagePreview.token) return;
    imagePreview.phase = "error";
    ui.imagePreviewStatus.textContent = "图片加载失败，请关闭后重试。";
  }
}

function finishImagePreviewClose(restoreFocus = true) {
  ++imagePreview.token;
  imagePreview.phase = "closed";
  cancelImagePreviewAnimation();
  imagePreview.pointers.clear();
  imagePreview.gesture = imagePreview.tap = imagePreview.backdropPointer = imagePreview.swipe = null;
  imagePreview.navigationRequest++;
  ui.imagePreviewVeil.getAnimations().forEach(animation => animation.cancel());
  ui.imagePreviewImage.classList.remove("is-interacting", "is-zoomed");
  ui.imagePreviewImage.hidden = true;
  ui.imagePreviewStatus.hidden = true;
  ui.imagePreviewAnnouncement.textContent = "";
  ui.imagePreviewDialog.classList.remove("has-navigation", "is-navigating");
  document.documentElement.classList.remove("image-preview-open");
  ui.detailImage.setAttribute("aria-expanded", "false");
  if (ui.imagePreviewDialog.open) ui.imagePreviewDialog.close();
  if (restoreFocus && ui.detailDialog.open) ui.detailImage.focus({ preventScroll: true });
  updateDetailNavigation();
}

function closeImagePreview({ immediate = false, restoreFocus = true } = {}) {
  if (imagePreview.phase === "closed") return;
  if (immediate) return finishImagePreviewClose(restoreFocus);
  if (imagePreview.phase === "closing") return;
  ++imagePreview.token; // Invalidate an in-flight decode before starting the exit.
  const hasImage = !ui.imagePreviewImage.hidden;
  imagePreview.phase = "closing";
  if (hasImage) {
    animateImagePreviewVeil(0, previewMotion("--motion-medium", 240));
    animateImagePreview(liveImagePreviewFrame(), imagePreviewSourceFrame(), previewMotion("--motion-medium", 240), () => finishImagePreviewClose(restoreFocus));
  } else {
    animateImagePreviewVeil(0, previewMotion("--motion-medium", 240), () => finishImagePreviewClose(restoreFocus));
  }
}

// During manipulation, update transforms directly so the picture follows the pointer.
function setImagePreviewZoom(nextZoom, focalPoint = null, smooth = false) {
  if (imagePreview.phase !== "open") return;
  const from = liveImagePreviewFrame();
  const previousZoom = imagePreview.zoom;
  imagePreview.zoom = clampPreview(nextZoom, 1, IMAGE_PREVIEW_MAX_ZOOM);
  if (imagePreview.zoom === 1) {
    imagePreview.x = imagePreview.y = 0;
  } else if (focalPoint) {
    const stage = ui.imagePreviewStage.getBoundingClientRect();
    const ratio = imagePreview.zoom / previousZoom;
    imagePreview.x = (focalPoint.x - stage.left - stage.width / 2) * (1 - ratio) + imagePreview.x * ratio;
    imagePreview.y = (focalPoint.y - stage.top - stage.height / 2) * (1 - ratio) + imagePreview.y * ratio;
  }
  applyImagePreviewTransform();
  if (smooth) animateImagePreview(from, imagePreviewFrame(), 220);
  else cancelImagePreviewAnimation();
}

function resetImagePreviewTransform() {
  setImagePreviewZoom(1, null, true);
}

function beginImagePreviewGesture() {
  const points = [...imagePreview.pointers.values()];
  imagePreview.gesture = {
    points: points.map(point => ({ ...point })),
    zoom: imagePreview.zoom, x: imagePreview.x, y: imagePreview.y,
  };
}

function imagePreviewPointerDown(event) {
  if (imagePreview.phase === "closing" && (event.pointerType !== "mouse" || event.button === 0)) {
    openImagePreview(); // reverse-reopen from the live frame
    return;
  }
  // During the entry animation, let it settle: grabbing mid-entry would snap
  // the pan offset through clamp logic and look like a jump.
  if (imagePreview.phase !== "open" || (event.pointerType === "mouse" && event.button !== 0)) return;
  // Continue from the presentation transform if a double-click zoom was still settling.
  const current = new DOMMatrixReadOnly(getComputedStyle(ui.imagePreviewImage).transform);
  cancelImagePreviewAnimation();
  imagePreview.zoom = current.a;
  imagePreview.x = current.e;
  imagePreview.y = current.f;
  applyImagePreviewTransform();
  ui.imagePreviewImage.setPointerCapture(event.pointerId);
  imagePreview.pointers.set(event.pointerId, { x: event.clientX, y: event.clientY, startX: event.clientX, startY: event.clientY, time: performance.now(), moved: false });
  imagePreview.swipe = event.pointerType === "mouse" ? null : { pointerId: event.pointerId, startX: event.clientX, startY: event.clientY };
  if (imagePreview.pointers.size > 1) {
    imagePreview.tap = null;
    imagePreview.pointers.forEach(point => { point.moved = true; });
  }
  ui.imagePreviewImage.classList.add("is-interacting");
  beginImagePreviewGesture();
  event.preventDefault();
}

function imagePreviewPointerMove(event) {
  const point = imagePreview.pointers.get(event.pointerId);
  if (!point || imagePreview.phase !== "open") return;
  Object.assign(point, { x: event.clientX, y: event.clientY });
  point.moved ||= Math.hypot(point.x - point.startX, point.y - point.startY) > 6;
  const points = [...imagePreview.pointers.values()];
  const gesture = imagePreview.gesture;
  if (points.length > 1) {
    const [a, b] = points;
    const [startA, startB] = gesture.points;
    const startDistance = Math.max(1, Math.hypot(startA.x - startB.x, startA.y - startB.y));
    imagePreview.zoom = clampPreview(gesture.zoom * Math.hypot(a.x - b.x, a.y - b.y) / startDistance, 1, IMAGE_PREVIEW_MAX_ZOOM);
    const stage = ui.imagePreviewStage.getBoundingClientRect();
    const ratio = imagePreview.zoom / gesture.zoom;
    imagePreview.x = (a.x + b.x) / 2 - stage.left - stage.width / 2 - ((startA.x + startB.x) / 2 - stage.left - stage.width / 2 - gesture.x) * ratio;
    imagePreview.y = (a.y + b.y) / 2 - stage.top - stage.height / 2 - ((startA.y + startB.y) / 2 - stage.top - stage.height / 2 - gesture.y) * ratio;
  } else if (point.moved) {
    imagePreview.x = gesture.x + point.x - gesture.points[0].x;
    imagePreview.y = gesture.y + point.y - gesture.points[0].y;
  }
  applyImagePreviewTransform();
  event.preventDefault();
}

function imagePreviewPointerUp(event) {
  const point = imagePreview.pointers.get(event.pointerId);
  if (!point) return;
  const deltaX = point.x - point.startX;
  const deltaY = point.y - point.startY;
  const isSwipe = event.type === "pointerup"
    && event.pointerType !== "mouse"
    && imagePreview.zoom <= 1.01
    && Math.abs(deltaX) >= 56
    && Math.abs(deltaX) > Math.abs(deltaY) * 1.25;
  imagePreview.pointers.delete(event.pointerId);
  if (isSwipe && imagePreview.pointers.size === 0) {
    imagePreview.tap = null;
    imagePreview.gesture = null;
    imagePreview.swipe = null;
    ui.imagePreviewImage.classList.remove("is-interacting");
    navigatePreview(deltaX < 0 ? 1 : -1);
    return;
  }
  if (event.type === "pointerup" && event.pointerType === "touch" && !point.moved && performance.now() - point.time < 300) {
    const previous = imagePreview.tap;
    if (previous && performance.now() - previous.time < 300 && Math.hypot(point.x - previous.x, point.y - previous.y) < 30) {
      setImagePreviewZoom(imagePreview.zoom < 1.01 ? 2 : 1, point, true);
      imagePreview.tap = null;
    } else imagePreview.tap = { x: point.x, y: point.y, time: performance.now() };
  }
  if (imagePreview.pointers.size) beginImagePreviewGesture();
  else {
    imagePreview.gesture = null;
    imagePreview.swipe = null;
    ui.imagePreviewImage.classList.remove("is-interacting");
  }
}

function imagePreviewWheel(event) {
  event.preventDefault();
  const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? ui.imagePreviewStage.clientHeight : 1);
  setImagePreviewZoom(imagePreview.zoom * Math.exp(-clampPreview(delta, -500, 500) * .0015), { x: event.clientX, y: event.clientY });
}

function collapseRegenerationDrawer(drawer) {
  if (drawer.hidden || drawer.classList.contains("closing")) return;
  drawer.classList.add("closing");
  setTimeout(() => {
    drawer.hidden = true;
    drawer.classList.remove("closing");
  }, 200);
}

function closeRegenerationDrawers(restoreFocus = true) {
  const hadOpen = !ui.replayDrawer.hidden || !ui.variantDrawer.hidden;
  collapseRegenerationDrawer(ui.replayDrawer);
  collapseRegenerationDrawer(ui.variantDrawer);
  ui.reproduceImage.setAttribute("aria-expanded", "false");
  ui.variantButton.setAttribute("aria-expanded", "false");
  if (restoreFocus && hadOpen && regenerationTrigger && document.contains(regenerationTrigger))
    regenerationTrigger.focus({ preventScroll: true });
  regenerationTrigger = null;
}

function regenerationReasons(mode) {
  return regenerationOptions?.modes?.[mode]?.reasons || [];
}

function renderRegenerationOptions() {
  if (!regenerationOptions || !selectedRecord) return;
  const issues = regenerationOptions.resourceIssues || [];
  const issueText = issues.length
    ? `<strong>无法生成</strong><span>${issues.map((item) => `${escapeHtml(item.label)}：${escapeHtml(item.name)}`).join("<br>")}</span>`
    : `<strong>资源检查通过</strong><span>模型、已启用 LoRA、高清模型与采样资源均可用。</span>`;
  ui.replayStatus.dataset.state = issues.length ? "error" : "ok";
  ui.replayStatus.innerHTML = issueText;
  ui.variantStatus.dataset.state = issues.length ? "error" : "ok";
  ui.variantStatus.innerHTML = issueText;
  ui.replaySeedSummary.innerHTML = `<span><b>图像种子</b>${escapeHtml(selectedRecord.sample_seed)}</span><span><b>提示词种子</b>${escapeHtml(selectedRecord.prompt_seed)}</span>`;
  ui.confirmReplay.disabled = !regenerationOptions.modes?.replay?.available;
  for (const input of ui.redrawSections.querySelectorAll("input")) {
    const section = regenerationOptions.sections?.[input.value];
    input.disabled = !section?.canRedraw;
    input.checked = false;
    input.closest("label").hidden = !section?.canRedraw;
  }
  updateVariantDrawer();
}

async function loadRegenerationOptions() {
  if (!selectedRecord) return null;
  if (regenerationOptions) return regenerationOptions;
  const requestId = ++regenerationRequest;
  ui.replayStatus.dataset.state = "pending";
  ui.replayStatus.textContent = "正在检查历史记录与本地资源…";
  ui.variantStatus.dataset.state = "pending";
  ui.variantStatus.textContent = "正在检查历史记录与本地资源…";
  try {
    const value = await request(`/api/history/${selectedRecord.id}/regeneration-options`);
    if (requestId !== regenerationRequest || !selectedRecord) return null;
    regenerationOptions = value;
    renderRegenerationOptions();
    return value;
  } catch (error) {
    if (requestId !== regenerationRequest) return null;
    for (const status of [ui.replayStatus, ui.variantStatus]) {
      status.dataset.state = "error";
      status.textContent = error.message;
    }
    return null;
  }
}

async function openRegenerationDrawer(kind, trigger) {
  const drawer = kind === "replay" ? ui.replayDrawer : ui.variantDrawer;
  const wasOpen = !drawer.hidden || drawer.classList.contains("closing");
  closeRegenerationDrawers(false);
  if (wasOpen) {
    trigger.focus({ preventScroll: true });
    return;
  }
  regenerationTrigger = trigger;
  drawer.classList.remove("closing");
  drawer.hidden = false;
  trigger.setAttribute("aria-expanded", "true");
  await loadRegenerationOptions();
  const focusTarget = kind === "replay" ? ui.confirmReplay : ui.variantModes.querySelector("input:checked");
  focusTarget?.focus({ preventScroll: true });
}

function selectedRegenerationMode() {
  return ui.variantModes.querySelector('input[name="regenerationMode"]:checked')?.value || "prompt_variant";
}

function selectedRedrawSections() {
  return [...ui.redrawSections.querySelectorAll("input:checked")].map((input) => input.value);
}

let redrawSectionsAnim = null;
function setRedrawSectionsVisible(visible) {
  const el = ui.redrawSections;
  // No-op when the requested state already matches; importantly this avoids
  // cancelling an in-flight entry/exit animation on repeated redraws.
  if (visible === !el.hidden) return;
  redrawSectionsAnim?.cancel();
  redrawSectionsAnim = null;
  if (visible) {
    el.hidden = false;
    redrawSectionsAnim = el.animate(
      [{ opacity: 0, transform: "translateY(-6px)" }, { opacity: 1, transform: "none" }],
      { duration: imagePreviewReducedMotion() ? 60 : 200, easing: "cubic-bezier(.2,.8,.2,1)", fill: "both" },
    );
  } else {
    redrawSectionsAnim = el.animate(
      [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(-6px)" }],
      { duration: imagePreviewReducedMotion() ? 60 : 160, easing: "cubic-bezier(.4,0,1,1)", fill: "both" },
    );
    redrawSectionsAnim.finished.then(() => { el.hidden = true; }).catch(() => {});
  }
}

function updateVariantDrawer() {
  const mode = selectedRegenerationMode();
  const sections = selectedRedrawSections();
  setRedrawSectionsVisible(mode === "content_redraw");
  const labels = {
    prompt_variant: "生成同提示词变体",
    content_redraw: "重新抽取所选内容",
    settings_reroll: "按此配置再抽",
  };
  ui.confirmVariant.textContent = labels[mode];
  const available = Boolean(regenerationOptions?.modes?.[mode]?.available);
  ui.confirmVariant.disabled = !available || (mode === "content_redraw" && !sections.length);
  const reasons = regenerationReasons(mode);
  if (reasons.length && !(regenerationOptions?.resourceIssues || []).length) {
    ui.variantStatus.dataset.state = "error";
    ui.variantStatus.innerHTML = `<strong>当前方式不可用</strong><span>${reasons.map(escapeHtml).join("<br>")}</span>`;
  }
}

async function submitRegeneration(mode, count = 1, sections = []) {
  if (!selectedRecord || submitInFlight) return false;
  submitInFlight = true;
  ui.confirmReplay.disabled = true;
  ui.confirmVariant.disabled = true;
  try {
    const body = mode === "replay" ? { mode } : { mode, count };
    if (mode === "content_redraw") body.sections = sections;
    const state = await request(`/api/history/${selectedRecord.id}/regenerate`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    toast(state.status === "queued" ? `已加入队列,第 ${state.position} 位` : "批次已开始");
    closeRegenerationDrawers(false);
    ui.detailDialog.close();
    return true;
  } catch (error) {
    toast(error.message);
    regenerationOptions = null;
    await loadRegenerationOptions();
    return false;
  } finally {
    submitInFlight = false;
    try {
      renderBatchPayload(await request("/api/batches/current"));
    } catch {
      ui.startButton.disabled = !ui.connection.classList.contains("online");
    }
    if (regenerationOptions) renderRegenerationOptions();
  }
}

function selectionHas(section, id) {
  const selection = draft.pools[section];
  return selection.mode === "all" ? !selection.excluded_ids.includes(id) : selection.ids.includes(id);
}
function toggleSelection(section, id, checked) {
  const selection = draft.pools[section];
  if (selection.mode === "all")
    selection.excluded_ids = checked
      ? selection.excluded_ids.filter((value) => value !== id)
      : [...new Set([...selection.excluded_ids, id])];
  else if (checked) selection.ids = [...new Set([...selection.ids, id])];
  else selection.ids = selection.ids.filter((value) => value !== id);
  renderPoolItems();
  renderDimensions();
  updatePoolOverview();
  updatePoseConflict();
  updateFavoriteSelectionButton();
  schedulePersist();
}

function favoriteKey(item) {
  return String(item.favorite_key || "");
}
function favoriteMap() {
  const map = new Map();
  for (const item of favoritesData.items || []) {
    const key = activeSection === "character" ? String(item.name || item.id || "") : String(item.id || item.name || "");
    if (key) map.set(key, item);
  }
  return map;
}
function isFavorite(item) {
  return Boolean(favoriteMap().get(favoriteKey(item))?.groupIds?.length);
}

async function loadFavorites(section = activeSection) {
  try {
    favoritesData = await request(`/api/favorites/${section}`);
    favoritesAvailable = true;
  } catch (error) {
    favoritesData = { groups: [], items: [], favorite_keys: [] };
    favoritesAvailable = false;
    if (currentView().filters.collection) currentView().filters.collection = "";
    if (currentView().sort === "favorite-first") currentView().sort = "";
    toast(`收藏不可用：${error.message}`);
  }
  updateFavoriteSelectionButton();
}
async function loadCustomGroups(section = activeSection) {
  try {
    customGroups = (await request(`/api/custom-groups/${section}`)).groups || [];
    if (!customTreeInitialized.has(section)) {
      collapsedCustomGroups[section] = new Set(
        customGroups.filter((group) => group.kind !== "group").map((group) => group.id),
      );
      customTreeInitialized.add(section);
      persistCustomTree();
    }
    if (currentView().filters.customGroup && !customGroup(currentView().filters.customGroup)) {
      currentView().filters.customGroup = "";
    }
    const activeGroup = customGroup(currentView().filters.customGroup);
    let ancestor = activeGroup?.parentId ? customGroup(activeGroup.parentId) : null;
    while (ancestor) {
      collapsedCustomGroups[section].delete(ancestor.id);
      ancestor = ancestor.parentId ? customGroup(ancestor.parentId) : null;
    }
  } catch (error) {
    customGroups = [];
    toast(`自定义分组不可用：${error.message}`);
  }
}

let drawerTrigger = null;
async function openPool(section) {
  activeSection = section;
  poolPage = 1;
  const view = currentView();
  drawerTrigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  // 关闭态的抽屉带 inert(不进 Tab 序列);打开时移除并把焦点移入抽屉。
  ui.poolDrawer.removeAttribute("inert");
  ui.poolDrawer.classList.add("open");
  ui.poolDrawer.setAttribute("aria-hidden", "false");
  clearTimeout(backdropCloseTimer);
  ui.drawerBackdrop.classList.remove("closing");
  ui.drawerBackdrop.hidden = false;
  ui.poolTitle.textContent = `${SECTION_META[section].label}池`;
  ui.poolKicker.textContent = "PROMPT POOL";
  ui.poolSearch.value = view.query;
  ui.poolSort.value = view.sort;
  ui.poolLanguage.value = view.language;
  ui.selectedOnly.checked = view.selectedOnly;
  ui.poolSearch.focus({ preventScroll: true });
  await Promise.all([loadFavorites(section), loadCustomGroups(section)]);
  await loadPool();
  schedulePersist();
}
let backdropCloseTimer = null;
function hideDrawerBackdrop() {
  clearTimeout(backdropCloseTimer);
  ui.drawerBackdrop.classList.add("closing");
  backdropCloseTimer = setTimeout(() => {
    ui.drawerBackdrop.hidden = true;
    ui.drawerBackdrop.classList.remove("closing");
  }, 300);
}

function closePool() {
  currentView().scrollTop = ui.poolGrid.scrollTop;
  setPoolSidebarOpen(false);
  ui.poolDrawer.classList.remove("open");
  ui.poolDrawer.setAttribute("aria-hidden", "true");
  ui.poolDrawer.setAttribute("inert", "");
  hideDrawerBackdrop();
  if (drawerTrigger && document.contains(drawerTrigger)) drawerTrigger.focus({ preventScroll: true });
  drawerTrigger = null;
  schedulePersist();
}
function setPoolSidebarOpen(open) {
  ui.poolSidebar.classList.toggle("mobile-open", open);
  ui.togglePoolSidebar.setAttribute("aria-expanded", String(open));
  ui.togglePoolSidebar.title = open ? "关闭分类导航" : "打开分类导航";
  ui.togglePoolSidebar.setAttribute("aria-label", ui.togglePoolSidebar.title);
}

function poolQueryBody() {
  const view = currentView();
  return {
    page: poolPage,
    limit: 48,
    q: view.query,
    sort: view.sort,
    collection: view.filters.collection,
    custom_group: view.filters.customGroup,
    categories: view.filters.categories,
    traits: view.filters.traits,
    gender: view.filters.gender,
    hair: view.filters.hair,
    eye: view.filters.eye,
    series: view.filters.series,
    blocked_only: view.blockedOnly ? "1" : "0",
  };
}
async function loadPool() {
  const requestId = ++poolRequest;
  const view = currentView();
  try {
    const query = poolQueryBody();
    let data;
    if (view.selectedOnly)
      data = await request(`/api/pools/${activeSection}/query`, {
        method: "POST",
        body: JSON.stringify({ ...query, selection: draft.pools[activeSection] }),
      });
    else {
      const params = new URLSearchParams({
        page: query.page,
        limit: query.limit,
        q: query.q,
        sort: query.sort,
        collection: query.collection,
        custom_group: query.custom_group,
        gender: query.gender,
        hair: query.hair,
        eye: query.eye,
        series: query.series,
        blocked_only: query.blocked_only,
      });
      query.categories.forEach((value) => params.append("category", value));
      query.traits.forEach((value) => params.append("trait", value));
      data = await request(`/api/pools/${activeSection}?${params}`);
    }
    if (requestId !== poolRequest) return;
    poolItems = data.items || [];
    poolTotal = Number(data.total) || 0;
    poolMatchingIds = Array.isArray(data.matching_ids)
      ? data.matching_ids.map((id) => String(id)).filter(Boolean)
      : poolItems.map((item) => String(item.id)).filter(Boolean);
    poolFacets = data.facets || {};
    poolPages = data.pages;
    poolPage = data.page;
    if (activeSection === "pose") {
      poolItems.forEach((item) => poseItemCache.set(item.id, item));
      if (data.pose_conflicts && typeof data.pose_conflicts === "object") {
        for (const [id, meta] of Object.entries(data.pose_conflicts)) {
          if (!poseItemCache.has(id) && meta && typeof meta === "object") {
            poseItemCache.set(id, meta);
          }
        }
      }
    }
    ui.poolPageLabel.textContent = `${data.page} / ${data.pages}`;
    ui.poolPrev.disabled = data.page <= 1;
    ui.poolNext.disabled = data.page >= data.pages;
    updatePoolMetaText();
    renderPoolSidebar();
    renderPoolItems();
    updatePoseConflict();
    requestAnimationFrame(() => {
      if (view.scrollTop && poolPage === 1) {
        ui.poolGrid.scrollTop = view.scrollTop;
        view.scrollTop = 0;
      }
    });
  } catch (error) {
    toast(error.message);
  }
}

function sidebarSection(title, items, kind, activeValues, multi = false) {
  if (!items?.length) return null;
  const section = document.createElement("section");
  section.className = "facet-section";
  section.innerHTML = `<h3>${escapeHtml(title)}</h3><div></div>`;
  const body = section.querySelector("div");
  const active = new Set(Array.isArray(activeValues) ? activeValues : [activeValues].filter(Boolean));
  for (const item of items) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = active.has(item.value) ? "active" : "";
    // 英文优先显示规范值;中文优先/双语显示服务端给出的中文标签(无中文时回退英文)
    const label = currentView().language === "en" ? item.label : item.label_zh || item.label;
    button.innerHTML = `<span>${escapeHtml(label)}</span><small>${item.count ?? ""}</small>`;
    button.addEventListener("click", () => {
      const filters = currentView().filters;
      if (multi) {
        const values = new Set(filters[kind] || []);
        values.has(item.value) ? values.delete(item.value) : values.add(item.value);
        filters[kind] = [...values];
      } else filters[kind] = filters[kind] === item.value ? "" : item.value;
      poolPage = 1;
      schedulePersist();
      loadPool();
    });
    body.append(button);
  }
  return section;
}

function favoriteChildren(parentId) {
  return (favoritesData.groups || []).filter((group) => (group.parentId || null) === (parentId || null));
}
function favoriteGroup(id) {
  return (favoritesData.groups || []).find((group) => group.id === id) || null;
}
function favoriteDescendantIds(groupId) {
  const ids = new Set();
  const pending = [groupId];
  while (pending.length) {
    const id = pending.pop();
    if (ids.has(id)) continue;
    ids.add(id);
    favoriteChildren(id).forEach((group) => pending.push(group.id));
  }
  return ids;
}
function favoriteGroupPath(group) {
  const names = [];
  const seen = new Set();
  let current = group;
  while (current && !seen.has(current.id)) {
    seen.add(current.id);
    names.unshift(current.id === "default" ? "我的收藏" : current.name);
    current = current.parentId ? favoriteGroup(current.parentId) : null;
  }
  return names.join(" / ");
}
function customChildren(parentId) {
  return customGroups.filter((group) => (group.parentId || null) === (parentId || null));
}
function customGroup(id) {
  return customGroups.find((group) => group.id === id) || null;
}
function customDescendantIds(groupId) {
  const ids = new Set();
  const pending = [groupId];
  while (pending.length) {
    const id = pending.pop();
    if (ids.has(id)) continue;
    ids.add(id);
    customChildren(id).forEach((group) => pending.push(group.id));
  }
  return ids;
}
function customGroupPath(group) {
  const names = [];
  const seen = new Set();
  let current = group;
  while (current && !seen.has(current.id)) {
    seen.add(current.id);
    names.unshift(current.name);
    current = current.parentId ? customGroup(current.parentId) : null;
  }
  return names.join(" / ");
}
function persistFavoriteTree() {
  const value = Object.fromEntries(SECTIONS.map((section) => [section, [...collapsedFavoriteGroups[section]]]));
  localStorage.setItem(GROUP_TREE_KEY, JSON.stringify(value));
}
function persistCustomTree() {
  const value = Object.fromEntries(SECTIONS.map((section) => [section, [...collapsedCustomGroups[section]]]));
  localStorage.setItem(CUSTOM_GROUP_TREE_KEY, JSON.stringify(value));
}
function focusFavoriteTreeRow(groupId) {
  queueMicrotask(() => {
    const row = ui.poolSidebar.querySelector(`.favorite-tree-row[data-group-id="${CSS.escape(groupId)}"]`);
    if (!row) return;
    ui.poolSidebar.querySelectorAll('.favorite-tree [role="treeitem"]').forEach((item) => {
      item.tabIndex = item === row ? 0 : -1;
    });
    row.focus();
  });
}
// Rows belonging to a group's descendant set, looked up pre-render.
function treeRowsForGroups(ids) {
  return [...ui.poolSidebar.querySelectorAll(".favorite-tree-row[data-group-id]")]
    .filter((row) => ids.has(row.dataset.groupId));
}
function animateTreeRowsIn(rows) {
  if (imagePreviewReducedMotion()) return;
  rows.forEach((row, index) => {
    row.animate(
      [{ opacity: 0, transform: "translateX(-8px)" }, { opacity: 1, transform: "none" }],
      { duration: 240, delay: Math.min(index * 30, 150), easing: "cubic-bezier(.32,.72,0,1)", fill: "both" },
    );
  });
}
function animateTreeRowsOut(rows, done) {
  if (!rows.length || imagePreviewReducedMotion()) return done();
  let remaining = rows.length;
  const finish = () => { if (--remaining <= 0) done(); };
  rows.forEach((row) => {
    row.animate(
      [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateX(-8px)" }],
      { duration: 160, easing: "cubic-bezier(.4,0,1,1)", fill: "both" },
    ).finished.then(finish).catch(finish);
  });
}
// Re-render the sidebar and play an entry animation on rows that did not exist
// before the render (i.e. freshly expanded children).
function renderPoolSidebarAnimated(enteredIds = new Set()) {
  const before = new Set(
    [...ui.poolSidebar.querySelectorAll(".favorite-tree-row[data-group-id]")].map((row) => row.dataset.groupId),
  );
  renderPoolSidebar();
  const fresh = enteredIds.size
    ? treeRowsForGroups(enteredIds).filter((row) => !before.has(row.dataset.groupId))
    : [];
  animateTreeRowsIn(fresh);
}

function toggleFavoriteTreeGroup(groupId, restoreFocus = false) {
  const collapsed = collapsedFavoriteGroups[activeSection];
  const collapsing = !collapsed.has(groupId);
  const descendants = favoriteDescendantIds(groupId);
  if (collapsing) {
    collapsed.add(groupId);
    persistFavoriteTree();
    animateTreeRowsOut(treeRowsForGroups(descendants), () => {
      renderPoolSidebar();
      if (restoreFocus) focusFavoriteTreeRow(groupId);
    });
    return;
  }
  collapsed.delete(groupId);
  persistFavoriteTree();
  renderPoolSidebarAnimated(descendants);
  if (restoreFocus) focusFavoriteTreeRow(groupId);
}
function focusCustomTreeRow(groupId) {
  queueMicrotask(() => {
    const tree = ui.poolSidebar.querySelector(".custom-group-tree");
    const row = tree?.querySelector(`.favorite-tree-row[data-group-id="${CSS.escape(groupId)}"]`);
    if (!row) return;
    tree.querySelectorAll('[role="treeitem"]').forEach((item) => {
      item.tabIndex = item === row ? 0 : -1;
    });
    row.focus();
  });
}
function toggleCustomTreeGroup(groupId, restoreFocus = false) {
  const collapsed = collapsedCustomGroups[activeSection];
  const collapsing = !collapsed.has(groupId);
  const descendants = customDescendantIds(groupId);
  if (collapsing) {
    collapsed.add(groupId);
    persistCustomTree();
    animateTreeRowsOut(treeRowsForGroups(descendants), () => {
      renderPoolSidebar();
      if (restoreFocus) focusCustomTreeRow(groupId);
    });
    return;
  }
  collapsed.delete(groupId);
  persistCustomTree();
  renderPoolSidebarAnimated(descendants);
  if (restoreFocus) focusCustomTreeRow(groupId);
}
function renderFavoriteTree(container, view) {
  container.className = "favorite-tree";
  container.setAttribute("role", "tree");
  container.setAttribute("aria-label", "收藏分组树");
  const allRow = document.createElement("div");
  allRow.className = `favorite-tree-row favorite-all-row${view.filters.collection ? "" : " active"}`;
  allRow.setAttribute("role", "treeitem");
  allRow.setAttribute("aria-level", "1");
  allRow.tabIndex = view.filters.collection ? -1 : 0;
  allRow.innerHTML = `<span class="tree-spacer" aria-hidden="true"></span><button type="button" class="group-select"><span>全部${escapeHtml(SECTION_META[activeSection].label)}</span><small>${config.catalog?.counts?.[activeSection] || ""}</small></button><span></span>`;
  allRow.querySelector(".group-select").addEventListener("click", () => {
    view.filters.collection = "";
    poolPage = 1;
    loadPool();
    schedulePersist();
    renderPoolSidebar();
  });
  container.append(allRow);

  const collapsed = collapsedFavoriteGroups[activeSection];
  const appendGroup = (group, depth) => {
    const children = favoriteChildren(group.id);
    const isCollapsed = collapsed.has(group.id);
    const active = view.filters.collection === group.id;
    const row = document.createElement("div");
    row.className = `favorite-tree-row${active ? " active" : ""}`;
    row.dataset.groupId = group.id;
    row.dataset.parentId = group.parentId || "";
    row.style.setProperty("--tree-depth", String(Math.min(depth, 4)));
    row.title = favoriteGroupPath(group);
    row.setAttribute("role", "treeitem");
    row.setAttribute("aria-level", String(depth + 1));
    row.setAttribute("aria-selected", String(active));
    if (children.length) row.setAttribute("aria-expanded", String(!isCollapsed));
    row.tabIndex = active ? 0 : -1;
    const disclosure = document.createElement(children.length ? "button" : "span");
    disclosure.className = children.length ? "tree-disclosure" : "tree-spacer";
    if (children.length) {
      disclosure.type = "button";
      disclosure.tabIndex = -1;
      disclosure.title = isCollapsed ? "展开子分组" : "折叠子分组";
      disclosure.setAttribute("aria-label", disclosure.title);
      disclosure.textContent = "›";
      disclosure.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleFavoriteTreeGroup(group.id, true);
      });
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = "group-select";
    button.innerHTML = `<span>${escapeHtml(group.id === "default" ? "我的收藏" : group.name)}</span><small>${group.totalCount ?? 0}</small>`;
    button.addEventListener("click", () => {
      view.filters.collection = group.id;
      poolPage = 1;
      loadPool();
      schedulePersist();
      renderPoolSidebar();
    });
    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "collection-edit";
    edit.title = group.isSystem ? "管理子分组" : "管理收藏分组";
    edit.setAttribute("aria-label", `${edit.title} ${group.id === "default" ? "我的收藏" : group.name}`);
    edit.textContent = "···";
    edit.addEventListener("click", (event) => {
      event.stopPropagation();
      openGroupDialog(group);
    });
    row.append(disclosure, button, edit);
    container.append(row);
    if (!isCollapsed) children.forEach((child) => appendGroup(child, depth + 1));
  };
  favoriteChildren(null).forEach((group) => appendGroup(group, 0));
}
function renderCustomTree(container, view) {
  container.className = "favorite-tree custom-group-tree";
  container.setAttribute("role", "tree");
  container.setAttribute("aria-label", "自定义分组树");
  const allRow = document.createElement("div");
  allRow.className = `favorite-tree-row favorite-all-row${view.filters.customGroup ? "" : " active"}`;
  allRow.dataset.groupId = "";
  allRow.setAttribute("role", "treeitem");
  allRow.setAttribute("aria-level", "1");
  allRow.tabIndex = view.filters.customGroup ? -1 : 0;
  allRow.innerHTML = '<span class="tree-spacer" aria-hidden="true"></span><button type="button" class="group-select"><span>不限分组</span><small></small></button><span></span>';
  allRow.querySelector(".group-select").addEventListener("click", async () => {
    view.filters.customGroup = "";
    poolPage = 1;
    schedulePersist();
    renderPoolSidebar();
    focusCustomTreeRow("");
    await loadPool();
    if (!view.filters.customGroup) focusCustomTreeRow("");
  });
  container.append(allRow);

  const collapsed = collapsedCustomGroups[activeSection];
  const appendGroup = (group, depth) => {
    const children = customChildren(group.id);
    const isCollapsed = collapsed.has(group.id);
    const active = view.filters.customGroup === group.id;
    const row = document.createElement("div");
    row.className = `favorite-tree-row${active ? " active" : ""}`;
    row.dataset.groupId = group.id;
    row.dataset.parentId = group.parentId || "";
    row.style.setProperty("--tree-depth", String(Math.min(depth, 4)));
    row.title = customGroupPath(group);
    row.setAttribute("role", "treeitem");
    row.setAttribute("aria-level", String(depth + 1));
    row.setAttribute("aria-selected", String(active));
    if (children.length) row.setAttribute("aria-expanded", String(!isCollapsed));
    row.tabIndex = active ? 0 : -1;
    const disclosure = document.createElement(children.length ? "button" : "span");
    disclosure.className = children.length ? "tree-disclosure" : "tree-spacer";
    if (children.length) {
      disclosure.type = "button";
      disclosure.tabIndex = -1;
      disclosure.title = isCollapsed ? "展开子分组" : "折叠子分组";
      disclosure.setAttribute("aria-label", disclosure.title);
      disclosure.textContent = "›";
      disclosure.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleCustomTreeGroup(group.id, true);
      });
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = "group-select";
    button.innerHTML = `<span>${escapeHtml(group.name)}</span><small>${group.count || 0}</small>`;
    button.addEventListener("click", async () => {
      view.filters.customGroup = group.id;
      poolPage = 1;
      schedulePersist();
      renderPoolSidebar();
      focusCustomTreeRow(group.id);
      await loadPool();
      if (view.filters.customGroup === group.id) focusCustomTreeRow(group.id);
    });
    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "collection-edit";
    edit.title = group.kind === "group" ? "编辑自定义分组" : "编辑导入大项";
    edit.setAttribute("aria-label", `${edit.title} ${group.name}`);
    edit.textContent = "···";
    edit.addEventListener("click", (event) => {
      event.stopPropagation();
      openCustomGroupDialog(group);
    });
    row.append(disclosure, button, edit);
    container.append(row);
    if (!isCollapsed) children.forEach((child) => appendGroup(child, depth + 1));
  };
  customChildren(null).forEach((group) => appendGroup(group, 0));
}
function handleGroupTreeKeydown(event) {
  const row = event.target.closest('[role="treeitem"]');
  const tree = row?.closest(".favorite-tree");
  if (!row || !tree) return;
  const rows = [...tree.querySelectorAll('[role="treeitem"]')];
  const index = rows.indexOf(row);
  const groupId = row.dataset.groupId || "";
  const isCustom = tree.classList.contains("custom-group-tree");
  const group = groupId ? (isCustom ? customGroup(groupId) : favoriteGroup(groupId)) : null;
  const toggle = isCustom ? toggleCustomTreeGroup : toggleFavoriteTreeGroup;
  if (event.key === "ArrowDown" || event.key === "ArrowUp") {
    event.preventDefault();
    const next = rows[index + (event.key === "ArrowDown" ? 1 : -1)];
    if (next) {
      row.tabIndex = -1;
      next.tabIndex = 0;
      next.focus();
    }
  } else if (event.key === "ArrowRight" && group) {
    event.preventDefault();
    if (row.getAttribute("aria-expanded") === "false") toggle(groupId, true);
    else {
      const next = rows[index + 1];
      if (next) {
        row.tabIndex = -1;
        next.tabIndex = 0;
        next.focus();
      }
    }
  } else if (event.key === "ArrowLeft" && group) {
    event.preventDefault();
    if (row.getAttribute("aria-expanded") === "true") toggle(groupId, true);
    else if (group.parentId) {
      const parent = rows.find((item) => item.dataset.groupId === group.parentId);
      if (parent) {
        row.tabIndex = -1;
        parent.tabIndex = 0;
        parent.focus();
      }
    }
  } else if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    row.querySelector(".group-select")?.click();
  }
}

function renderPoolSidebar() {
  const view = currentView();
  const nav = document.createDocumentFragment();

  // 1. 隔离屏蔽池常驻入口(置于侧栏最上方)
  const vaultSection = document.createElement("section");
  vaultSection.className = "facet-section blocked-vault-section";
  const blockedCount = blockedPromptSets[activeSection]?.size || 0;
  vaultSection.innerHTML = `<div class="blocked-vault-bar"><button type="button" class="group-select blocked-vault-btn ${view.blockedOnly ? "active" : ""}" title="查看/恢复被隔离的预设"><span>🚫 隔离屏蔽池</span><small class="pill-badge">${blockedCount}</small></button></div>`;
  vaultSection.querySelector(".blocked-vault-btn").addEventListener("click", () => {
    view.blockedOnly = !view.blockedOnly;
    if (view.blockedOnly) {
      // 隔离池视图与收藏/自定义分组互斥,避免空结果。
      view.filters.collection = "";
      view.filters.customGroup = "";
    }
    poolPage = 1;
    schedulePersist();
    loadPool();
  });
  nav.append(vaultSection);

  const collections = document.createElement("section");
  collections.className = "facet-section collections";
  collections.innerHTML = `<div class="facet-heading"><h3>收藏分组</h3><button type="button" title="新建收藏分组" aria-label="新建收藏分组">+</button></div><div></div>`;
  collections.querySelector(".facet-heading button").disabled = !favoritesAvailable;
  collections.querySelector(".facet-heading button").addEventListener("click", () => openGroupDialog());
  const collectionBody = collections.lastElementChild;
  renderFavoriteTree(collectionBody, view);
  nav.append(collections);
  const customSection = document.createElement("section");
  customSection.className = "facet-section custom-group-section";
  customSection.innerHTML = `<div class="facet-heading"><h3>自定义分组</h3><button type="button" title="新建自定义分组" aria-label="新建自定义分组">+</button></div><div></div>`;
  customSection.querySelector(".facet-heading button").addEventListener("click", () => openCustomGroupDialog());
  const customBody = customSection.lastElementChild;
  renderCustomTree(customBody, view);
  nav.append(customSection);
  if (activeSection === "character") {
    nav.append(sidebarSection("角色性别", poolFacets.gender, "gender", view.filters.gender));
    nav.append(sidebarSection("角色发色", poolFacets.hair, "hair", view.filters.hair));
    nav.append(sidebarSection("角色瞳色", poolFacets.eye, "eye", view.filters.eye));
    nav.append(sidebarSection("热门作品系列", poolFacets.series, "series", view.filters.series));
  } else {
    const labels = NATIVE_FACET_LABELS[activeSection];
    nav.append(sidebarSection(labels.categories, poolFacets.categories, "categories", view.filters.categories, true));
    nav.append(sidebarSection(labels.traits, poolFacets.traits, "traits", view.filters.traits, true));
  }
  ui.poolSidebar.replaceChildren(nav);
}

function displayTitle(item) {
  const lang = currentView().language;
  // 角色条目:title 是罗马字原名,title_zh 来自内置译名表(未收录时为空)。
  if (item.section === "character") {
    const zh = item.title_zh || "";
    if (lang === "en" || !zh) return item.title;
    if (lang === "bilingual") return `${zh} / ${item.title}`;
    return zh;
  }
  if (lang === "en") return item.subtitle || item.title;
  if (lang === "bilingual" && item.subtitle && item.subtitle !== item.title) return `${item.title} / ${item.subtitle}`;
  return item.title;
}
function seriesDisplay(item) {
  if (!item.copyright) return "";
  if (currentView().language === "en") return item.copyright;
  return item.subtitle_zh || item.copyright;
}
function categoryDisplay(value) {
  // 双语分类「中文 (English)」按语言偏好取半边;纯中文/纯英文原样。
  const match = String(value ?? "").match(/^(.*?)\s*\(([^()]*)\)\s*$/);
  if (!match || !match[1].trim()) return String(value ?? "");
  return currentView().language === "en" ? match[2].trim() : match[1].trim();
}
function itemBadges(item) {
  const values = [];
  if (activeSection === "character") {
    values.push(item.gender === "1girl" ? "女性" : item.gender === "1boy" ? "男性" : "未标注");
    if (item.hair) values.push(`${item.hair} hair`);
    if (item.eye) values.push(`${item.eye} eyes`);
  } else {
    values.push(...(item.categories || []).slice(0, 1).map(categoryDisplay));
    values.push(...(item.traits || []).slice(0, 2));
  }
  return values.filter(Boolean);
}
function renderPoolItems() {
  const favMap = favoriteMap();
  const view = currentView();
  const isVault = Boolean(view.blockedOnly);
  ui.poolEmpty.hidden = poolItems.length > 0;
  ui.poolEmpty.textContent = isVault ? "隔离池中暂无屏蔽预设" : "没有匹配的提示词";
  ui.poolGrid.replaceChildren(
    ...poolItems.map((item) => {
      const article = document.createElement("article");
      const selected = selectionHas(activeSection, item.id);
      const savedFavorite = favMap.get(favoriteKey(item));
      const favorite = Boolean(savedFavorite?.groupIds?.length);
      const isBlocked = blockedPromptSets[activeSection]?.has(item.id) || false;
      article.className = `pool-item ${selected ? "selected" : ""}${favorite ? " favorite" : ""}${isBlocked ? " is-blocked-item" : ""}`;
      article.innerHTML = `<label><input type="checkbox" ${selected ? "checked" : ""}><span class="pool-thumb">${item.preview ? `<img loading="lazy" src="${escapeHtml(item.preview)}" alt="">` : "<span>+</span>"}</span><span class="pool-item-copy"><strong title="${escapeHtml(displayTitle(item))}">${escapeHtml(displayTitle(item))}</strong><span class="item-badges">${itemBadges(
        item,
      )
        .map((value) => `<em>${escapeHtml(value)}</em>`)
        .join(
          "",
        )}</span><small>${escapeHtml(savedFavorite?.nickname || seriesDisplay(item) || item.prompt || "自定义项")}</small></span></label><div class="item-tools"><button class="block-toggle ${isBlocked ? "blocked" : ""}" type="button" title="${isBlocked ? "移出屏蔽池（恢复可用）" : "加入屏蔽池（移出卡池并禁用）"}" aria-label="${isBlocked ? "移出屏蔽池" : "加入屏蔽池"}">${isBlocked ? "↩" : "🚫"}</button><button class="favorite-toggle ${favorite ? "active" : ""}" type="button" title="${favorite ? "取消收藏" : "加入收藏"}" aria-label="${favorite ? "取消收藏" : "加入收藏"}">${favorite ? "♥" : "♡"}</button><button class="favorite-settings" type="button" title="收藏设置" aria-label="收藏设置" ${favorite ? "" : "hidden"}>⋮</button><button class="item-edit" type="button" title="编辑自定义项" aria-label="编辑自定义项" ${item.builtin ? "hidden" : ""}>✎</button></div>`;
      article
        .querySelector("label input")
        .addEventListener("change", (event) => toggleSelection(activeSection, item.id, event.target.checked));
      article.querySelector(".block-toggle").addEventListener("click", async (event) => {
        event.stopPropagation();
        await toggleBlockItem(item);
      });
      article.querySelector("img")?.addEventListener("error", (event) => (event.target.style.display = "none"));
      article.querySelector(".favorite-toggle").disabled = !favoritesAvailable;
      article.querySelector(".favorite-toggle").addEventListener("click", (event) => {
        event.stopPropagation();
        toggleFavorite(item, !favorite);
      });
      article.querySelector(".favorite-settings").addEventListener("click", (event) => {
        event.stopPropagation();
        openFavoriteDialog(item);
      });
      article.querySelector(".item-edit").addEventListener("click", (event) => {
        event.stopPropagation();
        openCustom(item);
      });
      return article;
    }),
  );
  ui.poolSelectionLabel.textContent = `已选择 ${selectedCount(activeSection)} 项`;
  updatePoolMetaText();
  updateFavoriteSelectionButton();
  updateFilteredActionButtons();
}

// 统一维护「选中筛选」与「取消筛选」两个批量按钮的文案、计数、禁用态与悬浮提示。
// 依赖 poolMatchingIds（后端返回的跨页匹配集合）与当前已选状态，可在任意渲染周期安全调用。
function updateFilteredActionButtons() {
  const view = currentView();
  const blockedSet = blockedPromptSets[activeSection] || new Set();
  const candidates = (Array.isArray(poolMatchingIds) ? poolMatchingIds : [])
    .map((id) => String(id))
    .filter((id) => id && !blockedSet.has(id));

  const matchCount = candidates.length;
  let selectedInMatchCount = 0;
  for (const id of candidates) {
    if (selectionHas(activeSection, id)) selectedInMatchCount += 1;
  }
  const unselectedInMatchCount = matchCount - selectedInMatchCount;

  if (ui.selectFiltered) {
    ui.selectFiltered.disabled =
      Boolean(view.blockedOnly) || Boolean(view.selectedOnly) || unselectedInMatchCount === 0;
    ui.selectFiltered.textContent = matchCount > 0 ? `选中筛选 · ${matchCount}` : "选中筛选";
    ui.selectFiltered.title = view.blockedOnly
      ? "隔离池中的预设已被禁用，无法勾选"
      : view.selectedOnly
        ? "当前处于“仅看已选”视图，展示项均已选中"
        : unselectedInMatchCount > 0
          ? `将当前筛选出的全部 ${matchCount} 项叠加加入已选（跨页生效）`
          : matchCount > 0
            ? `当前筛选出的 ${matchCount} 项均已在选中列表中`
            : "当前无匹配项可选";
  }

  if (ui.deselectFiltered) {
    ui.deselectFiltered.disabled = Boolean(view.blockedOnly) || selectedInMatchCount === 0;
    ui.deselectFiltered.textContent =
      selectedInMatchCount > 0 ? `取消筛选 · ${selectedInMatchCount}` : "取消筛选";
    ui.deselectFiltered.title = view.blockedOnly
      ? "隔离池中的预设已被禁用，无需取消选择"
      : selectedInMatchCount > 0
        ? `从已选中移除当前筛选结果里的 ${selectedInMatchCount} 项（跨页生效）`
        : "当前筛选结果中没有已选中的项目";
  }
}

function updatePoolMetaText() {
  if (!ui.poolMeta) return;
  ui.poolMeta.textContent = `${poolTotal} 项可用 · ${selectedCount(activeSection)} 项已选${favoritesAvailable ? "" : " · 收藏离线"}`;
}

// 切换单个预设的屏蔽状态:加入隔离池时同步从当前已选集合中剔除。
async function toggleBlockItem(item) {
  try {
    const res = await request(`/api/blocked-prompts/${activeSection}/toggle`, {
      method: "POST",
      body: JSON.stringify({ id: item.id }),
    });
    if (!blockedPromptSets[activeSection]) blockedPromptSets[activeSection] = new Set();
    if (res.blocked) {
      blockedPromptSets[activeSection].add(item.id);
      // 关键防御:若该预设当前在已选集合中,立即移出。
      const selection = draft.pools[activeSection];
      if (selection.mode === "include") {
        selection.ids = selection.ids.filter((id) => id !== item.id);
      } else if (selection.mode === "all") {
        selection.excluded_ids = [...new Set([...selection.excluded_ids, item.id])];
      }
      toast(`已将【${displayTitle(item)}】移入隔离屏蔽池`);
    } else {
      blockedPromptSets[activeSection].delete(item.id);
      toast(`已将【${displayTitle(item)}】从屏蔽池恢复`);
    }
    renderDimensions();
    updatePoolOverview();
    updatePoseConflict();
    schedulePersist();
    // 重新拉取词库以更新界面(当前页可能因此少一项)。
    await loadPool();
  } catch (error) {
    toast(`操作失败: ${error.message}`);
  }
}

function updatePoseConflict() {
  if (activeSection !== "pose") {
    ui.poseConflict.hidden = true;
    return;
  }
  const selection = draft.pools.pose;
  if (selection.mode === "all" || Number(draft.counts.pose || 1) <= 1) {
    ui.poseConflict.hidden = true;
    return;
  }
  const selected = selection.ids.map((id) => poseItemCache.get(id)).filter(Boolean);
  const groups = new Map();
  for (const item of selected)
    for (const slot of item.conflict_slots || []) {
      if (!groups.has(slot)) groups.set(slot, []);
      groups.get(slot).push(item.title);
    }
  const conflicts = [...groups.entries()].filter(([, names]) => names.length > 1);
  if (!conflicts.length) {
    ui.poseConflict.hidden = true;
    return;
  }
  const labels = { hand_action: "手部动作", body_pose: "整体姿态", interaction: "双人互动" };
  ui.poseConflict.hidden = false;
  ui.poseConflict.innerHTML = `<strong>存在潜在姿势冲突</strong><span>${conflicts.map(([slot, names]) => `${escapeHtml(labels[slot] || slot)}：${names.map(escapeHtml).join("、")}`).join("；")}</span>`;
}

function reconcileFavoriteCollection() {
  const view = currentView();
  if (view.filters.collection && !favoriteGroup(view.filters.collection)) {
    view.filters.collection = "";
    schedulePersist();
    return true;
  }
  return false;
}
async function toggleFavorite(item, favorite) {
  try {
    favoritesData = await request(`/api/favorites/${activeSection}/item`, {
      method: "PUT",
      body: JSON.stringify({ id: item.id, favorite }),
    });
    favoritesAvailable = true;
    const resetCollection = reconcileFavoriteCollection();
    if (resetCollection || (!favorite && currentView().filters.collection)) await loadPool();
    else {
      renderPoolItems();
      renderPoolSidebar();
    }
    toast(favorite ? "已加入 Anima 收藏" : "已取消收藏");
  } catch (error) {
    toast(error.message);
  }
}
function orderedFavoriteGroups() {
  const result = [];
  const append = (group, depth) => {
    result.push({ group, depth });
    favoriteChildren(group.id).forEach((child) => append(child, depth + 1));
  };
  favoriteChildren(null).forEach((group) => append(group, 0));
  return result;
}
function openFavoriteDialog(item) {
  editingFavoriteItem = item;
  const saved = favoriteMap().get(favoriteKey(item)) || {};
  ui.favoriteTitle.textContent = displayTitle(item);
  ui.favoriteNickname.value = saved.nickname || "";
  ui.favoriteGroups.replaceChildren(
    ...orderedFavoriteGroups().map(({ group, depth }) => {
      const label = document.createElement("label");
      label.className = "favorite-group-check tree-check";
      label.style.setProperty("--tree-depth", String(Math.min(depth, 4)));
      label.title = favoriteGroupPath(group);
      label.innerHTML = `<input type="checkbox" value="${escapeHtml(group.id)}" ${(saved.groupIds || []).includes(group.id) ? "checked" : ""}><span>${escapeHtml(group.id === "default" ? "我的收藏" : group.name)}</span><small>${group.totalCount ?? 0}</small>`;
      return label;
    }),
  );
  ui.favoriteDialog.showModal();
}
function favoriteSelectionDefaultGroups() {
  const currentCollection = currentView().filters.collection;
  if (currentCollection && favoriteGroup(currentCollection)) return [currentCollection];
  return favoriteGroup("default") ? ["default"] : [];
}
function renderFavoriteSelectionGroups(selectedIds = favoriteSelectionDefaultGroups()) {
  const selected = new Set(selectedIds);
  ui.favoriteSelectionGroups.replaceChildren(
    ...orderedFavoriteGroups().map(({ group, depth }) => {
      const label = document.createElement("label");
      label.className = "favorite-group-check tree-check";
      label.style.setProperty("--tree-depth", String(Math.min(depth, 4)));
      label.title = favoriteGroupPath(group);
      label.innerHTML = `<input type="checkbox" value="${escapeHtml(group.id)}" ${selected.has(group.id) ? "checked" : ""}><span>${escapeHtml(group.id === "default" ? "我的收藏" : group.name)}</span><small>${group.totalCount ?? 0}</small>`;
      return label;
    }),
  );
}
function openFavoriteSelectionDialog() {
  if (!favoritesAvailable || !selectedCount(activeSection)) return;
  ui.favoriteSelectionTitle.textContent = `收藏${SECTION_META[activeSection].label}池本次选择`;
  ui.favoriteSelectionSummary.textContent = `将当前${SECTION_META[activeSection].label}池已选择的 ${selectedCount(activeSection)} 项加入收藏分组；已有收藏只追加分组，不覆盖备注。`;
  ui.favoriteSelectionGroupName.value = "";
  ui.favoriteSelectionError.hidden = true;
  ui.favoriteSelectionError.textContent = "";
  ui.confirmFavoriteSelection.disabled = false;
  ui.confirmFavoriteSelection.textContent = "收藏";
  renderFavoriteSelectionGroups();
  ui.favoriteSelectionDialog.showModal();
}
async function createFavoriteSelectionGroup() {
  const name = ui.favoriteSelectionGroupName.value.trim();
  if (!name) {
    ui.favoriteSelectionError.textContent = "请输入收藏分组名称";
    ui.favoriteSelectionError.hidden = false;
    return;
  }
  ui.createFavoriteSelectionGroup.disabled = true;
  try {
    favoritesData = await request(`/api/favorites/${activeSection}/groups`, {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    const selectedIds = [...ui.favoriteSelectionGroups.querySelectorAll("input:checked")].map((input) => input.value);
    const newGroup = (favoritesData.groups || []).find((group) => group.name === name && !group.isSystem);
    if (newGroup) selectedIds.push(newGroup.id);
    renderFavoriteSelectionGroups([...new Set(selectedIds)]);
    ui.favoriteSelectionGroupName.value = "";
    ui.favoriteSelectionError.hidden = true;
    renderPoolSidebar();
  } catch (error) {
    ui.favoriteSelectionError.textContent = error.message;
    ui.favoriteSelectionError.hidden = false;
  } finally {
    ui.createFavoriteSelectionGroup.disabled = false;
  }
}
async function saveFavoriteSelection(event) {
  event.preventDefault();
  const groupIds = [...ui.favoriteSelectionGroups.querySelectorAll("input:checked")].map((input) => input.value);
  if (!groupIds.length) {
    ui.favoriteSelectionError.textContent = "至少选择一个收藏分组";
    ui.favoriteSelectionError.hidden = false;
    return;
  }
  ui.confirmFavoriteSelection.disabled = true;
  ui.confirmFavoriteSelection.textContent = "收藏中…";
  try {
    const payload = await request(`/api/favorites/${activeSection}/selection`, {
      method: "POST",
      body: JSON.stringify({ selection: draft.pools[activeSection], groupIds }),
    });
    favoritesData = payload;
    ui.favoriteSelectionDialog.close();
    renderPoolItems();
    renderPoolSidebar();
    toast(`已收藏 ${payload.selectedCount || 0} 项：新增 ${payload.createdCount || 0} 项，更新 ${payload.updatedCount || 0} 项`);
  } catch (error) {
    ui.favoriteSelectionError.textContent = error.message;
    ui.favoriteSelectionError.hidden = false;
  } finally {
    ui.confirmFavoriteSelection.disabled = false;
    ui.confirmFavoriteSelection.textContent = "收藏";
  }
}
async function saveFavorite(event) {
  event.preventDefault();
  if (!editingFavoriteItem) return;
  const groupIds = [...ui.favoriteGroups.querySelectorAll("input:checked")].map((input) => input.value);
  try {
    favoritesData = await request(`/api/favorites/${activeSection}/item`, {
      method: "PUT",
      body: JSON.stringify({
        id: editingFavoriteItem.id,
        favorite: true,
        groupIds,
        nickname: ui.favoriteNickname.value,
      }),
    });
    ui.favoriteDialog.close();
    if (reconcileFavoriteCollection()) await loadPool();
    else {
      renderPoolItems();
      renderPoolSidebar();
    }
    toast("收藏设置已保存");
  } catch (error) {
    toast(error.message);
  }
}
async function removeFavorite() {
  if (!editingFavoriteItem) return;
  try {
    favoritesData = await request(`/api/favorites/${activeSection}/item`, {
      method: "PUT",
      body: JSON.stringify({ id: editingFavoriteItem.id, favorite: false }),
    });
    ui.favoriteDialog.close();
    reconcileFavoriteCollection();
    await loadPool();
    toast("已取消收藏");
  } catch (error) {
    toast(error.message);
  }
}

function openGroupDialog(group = null) {
  editingGroup = group;
  ui.groupId.value = group?.id || "";
  ui.groupName.value = group?.name || "";
  ui.groupDialogTitle.textContent = !group ? "新建收藏分组" : group.isSystem ? "管理我的收藏" : "编辑收藏分组";
  ui.groupNameField.hidden = Boolean(group?.isSystem);
  ui.groupName.required = !group?.isSystem;
  ui.deleteGroup.hidden = !group || group.isSystem;
  ui.importChildGroup.hidden = !group;
  ui.saveGroupButton.hidden = Boolean(group?.isSystem);
  ui.groupDialog.showModal();
}
async function saveGroup(event) {
  event.preventDefault();
  const id = ui.groupId.value;
  try {
    favoritesData = await request(
      id
        ? `/api/favorites/${activeSection}/groups/${encodeURIComponent(id)}`
        : `/api/favorites/${activeSection}/groups`,
      { method: id ? "PUT" : "POST", body: JSON.stringify({ name: ui.groupName.value }) },
    );
    ui.groupDialog.close();
    renderPoolSidebar();
    toast(id ? "收藏分组已更新" : "收藏分组已创建");
  } catch (error) {
    toast(error.message);
  }
}
function setChildGroupError(message = "") {
  ui.childGroupError.textContent = message;
  ui.childGroupError.hidden = !message;
}
function renderChildGroupSources() {
  const query = ui.childGroupSearch.value.trim().toLocaleLowerCase();
  const siblings = favoriteChildren(childGroupParent?.id);
  const available = customGroups.filter((group) => !query || group.name.toLocaleLowerCase().includes(query));
  ui.childGroupList.replaceChildren(
    ...available.map((group) => {
      const duplicate = siblings.some(
        (item) =>
          item.sourceCustomGroupId === group.id ||
          item.name.trim().toLocaleLowerCase() === group.name.trim().toLocaleLowerCase(),
      );
      const disabled = !group.count || duplicate;
      const label = document.createElement("label");
      label.className = `child-group-option${disabled ? " disabled" : ""}`;
      label.title = duplicate ? "当前父组下已经导入" : !group.count ? "空分组不能导入" : `导入 ${group.count} 项`;
      label.innerHTML = `<input type="radio" name="childGroupSource" value="${escapeHtml(group.id)}" ${selectedChildSource === group.id ? "checked" : ""} ${disabled ? "disabled" : ""}><span><strong>${escapeHtml(customGroupPath(group))}</strong><small>${duplicate ? "已导入" : !group.count ? "空分组" : `${group.count} 项 · 一次性快照`}</small></span>`;
      label.querySelector("input").addEventListener("change", () => {
        selectedChildSource = group.id;
        ui.confirmChildGroup.disabled = false;
        setChildGroupError();
      });
      return label;
    }),
  );
  ui.childGroupEmpty.textContent = customGroups.length ? "没有匹配的自定义分组。" : "当前分类还没有自定义分组。";
  ui.childGroupEmpty.hidden = available.length > 0;
}
function openChildGroupDialog(group = editingGroup) {
  if (!group) return;
  childGroupParent = group;
  selectedChildSource = "";
  ui.groupDialog.close();
  ui.childGroupTitle.textContent = `导入到“${group.id === "default" ? "我的收藏" : group.name}”`;
  ui.childGroupHint.textContent = "从当前提示词池的自定义分组创建一次性收藏快照，后续两边独立修改。";
  ui.childGroupSearch.value = "";
  ui.confirmChildGroup.disabled = true;
  setChildGroupError();
  renderChildGroupSources();
  ui.childGroupDialog.showModal();
}
async function importFavoriteChild(event) {
  event.preventDefault();
  if (!childGroupParent || !selectedChildSource || ui.confirmChildGroup.disabled) return;
  const label = ui.confirmChildGroup.textContent;
  ui.confirmChildGroup.disabled = true;
  ui.confirmChildGroup.textContent = "导入中…";
  try {
    favoritesData = await request(
      `/api/favorites/${activeSection}/groups/${encodeURIComponent(childGroupParent.id)}/children/import`,
      { method: "POST", body: JSON.stringify({ customGroupId: selectedChildSource }) },
    );
    collapsedFavoriteGroups[activeSection].delete(childGroupParent.id);
    persistFavoriteTree();
    ui.childGroupDialog.close();
    renderPoolSidebar();
    if (currentView().filters.collection === childGroupParent.id) await loadPool();
    toast("收藏子分组已导入");
  } catch (error) {
    setChildGroupError(error.message);
  } finally {
    ui.confirmChildGroup.disabled = !selectedChildSource;
    ui.confirmChildGroup.textContent = label;
  }
}

function deleteStat(label, value) {
  return `<div><strong>${Number(value) || 0}</strong><span>${escapeHtml(label)}</span></div>`;
}
function openDeleteGroupDialog(kind, group) {
  pendingGroupDelete = { kind, group };
  const favorite = kind === "favorite";
  const subtree = favorite ? favoriteDescendantIds(group.id) : customDescendantIds(group.id);
  const directCount = Number(group.directCount || 0);
  const affectedFavorites = favorite
    ? (favoritesData.items || []).filter((item) => (item.groupIds || []).some((id) => subtree.has(id)))
    : [];
  const exclusiveCount = favorite
    ? affectedFavorites.filter((item) => !(item.groupIds || []).some((id) => !subtree.has(id))).length
    : Number(group.exclusiveCount || 0);
  const totalCount = favorite ? affectedFavorites.length : Number(group.count || 0);
  const sharedCount = Math.max(0, totalCount - exclusiveCount);
  const childCount = Number(group.childCount || 0);
  const canDeleteItems = favorite ? Boolean(group.parentId && !childCount && directCount) : totalCount > 0;
  ui.groupDialog.close();
  ui.customGroupDialog.close();
  ui.deleteGroupTitle.textContent = `删除“${group.id === "default" ? "我的收藏" : group.name}”`;
  ui.deleteGroupSummary.textContent =
    subtree.size > 1
      ? `将删除当前父组及 ${subtree.size - 1} 个后代分组，${favorite ? "收藏" : "自定义提示词"}默认保留。`
      : "默认只删除分组结构，条目保持不变。";
  ui.deleteGroupStats.innerHTML = favorite
    ? `${deleteStat("分组", subtree.size)}${deleteStat("聚合收藏", totalCount)}${deleteStat("独占收藏", exclusiveCount)}${deleteStat("共享收藏", sharedCount)}`
    : `${deleteStat("分组", subtree.size)}${deleteStat("聚合条目", totalCount)}${deleteStat("可删除独占项", exclusiveCount)}${deleteStat("保留共享项", sharedCount)}`;
  ui.deleteGroupKeep.checked = true;
  ui.deleteGroupKeepHint.textContent = favorite
    ? `${exclusiveCount} 项失去最后分组的收藏会移入“我的收藏”，其余收藏保留现有分组。`
    : "所有自定义提示词都会保留，仅解除当前分组关联。";
  ui.deleteGroupItemsOption.hidden = !canDeleteItems;
  ui.deleteGroupItemsTitle.textContent = favorite
    ? `同时删除 ${exclusiveCount} 项独占收藏`
    : `同时删除 ${exclusiveCount} 项独占提示词`;
  ui.deleteGroupItemsHint.textContent = sharedCount
    ? `${sharedCount} 项共享条目只会解除当前分组关联。`
    : "没有共享条目。";
  ui.deleteGroupAllOption.hidden = favorite;
  ui.deleteGroupAllHint.textContent = sharedCount
    ? `不可撤销：将永久删除全部 ${totalCount} 项内容，其中 ${sharedCount} 项也属于其他分组。`
    : `不可撤销：将永久删除该分组子树中的全部 ${totalCount} 项内容。`;
  ui.deleteGroupError.hidden = true;
  ui.deleteGroupError.textContent = "";
  ui.confirmDeleteGroup.disabled = false;
  ui.confirmDeleteGroup.textContent = "删除";
  ui.deleteGroupDialog.showModal();
}
async function confirmGroupDelete(event) {
  event.preventDefault();
  if (!pendingGroupDelete || ui.confirmDeleteGroup.disabled) return;
  const { kind, group } = pendingGroupDelete;
  const deleteItems = !ui.deleteGroupItemsOption.hidden && ui.deleteGroupItems.checked;
  const deleteMode = ui.deleteGroupAll.checked ? "all" : deleteItems ? "exclusive" : "keep";
  ui.confirmDeleteGroup.disabled = true;
  ui.confirmDeleteGroup.textContent = "删除中…";
  ui.deleteGroupError.hidden = true;
  try {
    if (kind === "favorite") {
      const payload = await request(
        `/api/favorites/${activeSection}/groups/${encodeURIComponent(group.id)}?deleteItems=${deleteItems}`,
        { method: "DELETE" },
      );
      favoritesData = payload;
      if ((payload.deletedGroupIds || []).includes(currentView().filters.collection))
        currentView().filters.collection = "";
      collapsedFavoriteGroups[activeSection] = new Set(
        [...collapsedFavoriteGroups[activeSection]].filter((id) => !(payload.deletedGroupIds || []).includes(id)),
      );
      persistFavoriteTree();
      toast(
        deleteItems
          ? `已删除分组和 ${payload.deletedFavoriteCount || 0} 项独占收藏`
          : `已删除 ${payload.deletedGroupCount || 1} 个分组，条目已保留`,
      );
    } else {
      const payload = await request(
        `/api/custom-groups/${activeSection}/${encodeURIComponent(group.id)}?deleteMode=${deleteMode}`,
        { method: "DELETE" },
      );
      customGroups = payload.groups || [];
      const deletedIds = new Set(payload.deletedItemIds || []);
      const selection = draft.pools[activeSection];
      selection.ids = selection.ids.filter((id) => !deletedIds.has(id));
      selection.excluded_ids = selection.excluded_ids.filter((id) => !deletedIds.has(id));
      deletedIds.forEach((id) => poseItemCache.delete(id));
      const removedGroups = new Set(payload.deletedGroupIds || [group.id]);
      if (removedGroups.has(currentView().filters.customGroup)) currentView().filters.customGroup = "";
      collapsedCustomGroups[activeSection] = new Set(
        [...collapsedCustomGroups[activeSection]].filter((id) => !removedGroups.has(id)),
      );
      persistCustomTree();
      schedulePersist();
      toast(
        payload.deleteMode === "all"
          ? `已彻底删除分组和 ${payload.deletedItemCount || 0} 项关联内容`
          : payload.deleteMode === "exclusive"
            ? `已删除分组和 ${payload.deletedItemCount || 0} 项独占提示词`
            : "自定义分组已删除，条目已保留",
      );
    }
    ui.deleteGroupDialog.close();
    pendingGroupDelete = null;
    await loadPool();
    renderPoolSidebar();
    renderDimensions();
    updatePoolOverview();
  } catch (error) {
    ui.deleteGroupError.textContent = error.message;
    ui.deleteGroupError.hidden = false;
  } finally {
    ui.confirmDeleteGroup.disabled = false;
    ui.confirmDeleteGroup.textContent = "删除";
  }
}
function deleteFavoriteGroup() {
  if (editingGroup) openDeleteGroupDialog("favorite", editingGroup);
}

function selectCurrentPage(checked) {
  const view = currentView();
  // 处于隔离池视图时禁止批量勾选:池内预设已被禁用。
  if (view.blockedOnly) {
    toast("隔离池中的预设已被禁用，无法勾选");
    return;
  }

  const blockedSet = blockedPromptSets[activeSection] || new Set();
  for (const item of poolItems) {
    // 关键守卫:命中屏蔽池的条目绝对跳过,无法被选中。
    if (blockedSet.has(item.id)) continue;

    const selection = draft.pools[activeSection];
    if (selection.mode === "all")
      selection.excluded_ids = checked
        ? selection.excluded_ids.filter((value) => value !== item.id)
        : [...new Set([...selection.excluded_ids, item.id])];
    else if (checked) selection.ids = [...new Set([...selection.ids, item.id])];
    else selection.ids = selection.ids.filter((value) => value !== item.id);
  }
  renderPoolItems();
  renderDimensions();
  updatePoolOverview();
  updatePoseConflict();
  updateFavoriteSelectionButton();
  schedulePersist();
}

function selectFilteredItems() {
  const view = currentView();
  // 守卫 1: 处于隔离屏蔽池或“仅看已选”视图时不执行叠加
  if (view.blockedOnly) {
    toast("隔离池中的预设已被禁用，无法勾选");
    return;
  }
  if (view.selectedOnly) {
    toast("当前处于“仅看已选”视图，筛选结果均已在选中列表中");
    return;
  }

  const blockedSet = blockedPromptSets[activeSection] || new Set();
  // 守卫 2: 过滤空值与任何处于屏蔽池中的条目 ID
  const candidates = (Array.isArray(poolMatchingIds) ? poolMatchingIds : [])
    .map((id) => String(id))
    .filter((id) => id && !blockedSet.has(id));

  if (!candidates.length) {
    toast("当前筛选条件下没有可勾选的项");
    return;
  }

  if (!draft.pools[activeSection]) {
    draft.pools[activeSection] = { mode: "include", ids: [], excluded_ids: [] };
  }
  const selection = draft.pools[activeSection];
  let newlyAdded = 0;

  if (selection.mode === "all") {
    // 全选词库模式(mode: "all")下，已被用户手动取消勾选的项保存在 excluded_ids 中；
    // 叠加选中当前筛选结果，即把匹配项从 excluded_ids 中移除以恢复选中，已选中的保持不变。
    const candidateSet = new Set(candidates);
    const beforeLen = selection.excluded_ids.length;
    selection.excluded_ids = selection.excluded_ids.filter((id) => !candidateSet.has(String(id)));
    newlyAdded = beforeLen - selection.excluded_ids.length;
  } else {
    // 正选模式(mode: "include")下，基于用户已有选择叠加追加，已选中的无视且保持原顺序不变
    const existingSet = new Set(selection.ids.map((id) => String(id)));
    for (const id of candidates) {
      if (!existingSet.has(id)) {
        selection.ids.push(id);
        existingSet.add(id);
        newlyAdded += 1;
      }
    }
  }

  renderPoolItems();
  renderDimensions();
  updatePoolOverview();
  updatePoseConflict();
  updateFavoriteSelectionButton();
  schedulePersist();

  if (newlyAdded > 0) {
    const skippedCount = candidates.length - newlyAdded;
    toast(
      skippedCount > 0
        ? `已叠加选中 ${newlyAdded} 项（其余 ${skippedCount} 项已在选中列表中）`
        : `已选中当前筛选的全部 ${newlyAdded} 项`,
    );
  } else {
    toast(`当前筛选出的 ${candidates.length} 项均已在选中列表中`);
  }
}

// 与 selectFilteredItems 严格对称：把当前筛选结果中「已选中」的跨页条目从已选集合中批量移除。
async function deselectFilteredItems() {
  const view = currentView();
  // 守卫 1: 处于隔离屏蔽池视图时不执行操作
  if (view.blockedOnly) {
    toast("隔离池中的预设已被禁用，无需取消选择");
    return;
  }

  // 收集当前筛选条件下匹配的全部跨页条目 ID
  const candidates = (Array.isArray(poolMatchingIds) ? poolMatchingIds : [])
    .map((id) => String(id))
    .filter(Boolean);

  if (!candidates.length) {
    toast("当前筛选条件下没有可取消的项");
    return;
  }

  if (!draft.pools[activeSection]) {
    draft.pools[activeSection] = { mode: "include", ids: [], excluded_ids: [] };
  }
  const selection = draft.pools[activeSection];
  const candidateSet = new Set(candidates);
  let removedCount = 0;

  if (selection.mode === "all") {
    // 全选词库模式(mode: "all")下，取消选中当前筛选结果 = 将匹配项并入 excluded_ids 排除列表；
    // 原本已在 excluded_ids 中的未选项自动跳过。
    const excludedSet = new Set(selection.excluded_ids.map((id) => String(id)));
    for (const id of candidates) {
      if (!excludedSet.has(id)) {
        selection.excluded_ids.push(id);
        excludedSet.add(id);
        removedCount += 1;
      }
    }
  } else {
    // 正选模式(mode: "include")下，直接从 selection.ids 中剔除命中当前筛选结果的项；
    // 原本不在 selection.ids 中的未选项自然跳过，其余已选项保持原有顺序不变。
    const beforeLen = selection.ids.length;
    selection.ids = selection.ids.filter((id) => !candidateSet.has(String(id)));
    removedCount = beforeLen - selection.ids.length;
  }

  if (removedCount === 0) {
    toast("当前筛选结果中没有已选中的项");
    updateFilteredActionButtons();
    return;
  }

  renderDimensions();
  updatePoolOverview();
  updatePoseConflict();
  updateFavoriteSelectionButton();
  schedulePersist();

  // 若当前开启了“仅看已选”视图，被取消选中的项目应立即从视图中移除，需重置页码并重新拉取列表
  if (view.selectedOnly) {
    poolPage = 1;
    await loadPool();
  } else {
    renderPoolItems();
  }

  const skippedCount = candidates.length - removedCount;
  toast(
    skippedCount > 0
      ? `已取消选中 ${removedCount} 项（其余 ${skippedCount} 项原本未选中）`
      : `已取消选中当前筛选的全部 ${removedCount} 项`,
  );
}

function openCustom(item = null) {
  editingCustom = item;
  ui.customDialogTitle.textContent = item ? "编辑自定义项" : "新增自定义项";
  ui.customId.value = item?.id || "";
  ui.customTitle.value = item?.title || "";
  ui.customSubtitle.value = item?.subtitle || "";
  ui.customGender.value = item?.gender === "1girl" ? "female" : item?.gender === "1boy" ? "male" : "unknown";
  ui.customHair.value = item?.hair || "";
  ui.customEye.value = item?.eye || "";
  ui.customSeries.value = item?.copyright || "";
  ui.customCategory.value = item?.categories?.[0] || "";
  ui.customTraits.value = (item?.traits || []).join(", ");
  ui.customPrompt.value = item?.prompt || "";
  ui.customGenderField.hidden = activeSection !== "character";
  ui.customCharacterMeta.hidden = activeSection !== "character";
  ui.customPoseMeta.hidden = activeSection !== "pose";
  const selectedGroups = new Set(item?.group_ids || item?.groupIds || []);
  const leafGroups = customGroups.filter((group) => group.kind === "group");
  ui.customGroupChecks.replaceChildren(
    ...leafGroups.map((group) => {
      const label = document.createElement("label");
      label.className = "favorite-group-check";
      label.title = customGroupPath(group);
      label.innerHTML = `<input type="checkbox" value="${escapeHtml(group.id)}" ${selectedGroups.has(group.id) ? "checked" : ""}><span>${escapeHtml(customGroupPath(group))}</span>`;
      return label;
    }),
  );
  if (!leafGroups.length)
    ui.customGroupChecks.innerHTML = `<div class="inline-empty">尚未创建自定义分组，可在随机池侧栏新建。</div>`;
  ui.deleteCustom.hidden = !item;
  ui.customDialog.showModal();
}
async function saveCustom(event) {
  event.preventDefault();
  try {
    await normalizePromptFields({ custom_prompt: ui.customPrompt.value });
    const payload = {
      section: activeSection,
      title: ui.customTitle.value,
      subtitle: ui.customSubtitle.value,
      prompt: ui.customPrompt.value,
      gender: ui.customGender.value,
      hair: ui.customHair.value,
      eye: ui.customEye.value,
      copyright: ui.customSeries.value,
      categories: ui.customCategory.value ? [ui.customCategory.value] : [],
      traits: ui.customTraits.value
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean),
      groupIds: [...ui.customGroupChecks.querySelectorAll("input:checked")].map((input) => input.value),
    };
    const item = editingCustom
      ? await request(`/api/custom-prompts/${editingCustom.id}`, { method: "PUT", body: JSON.stringify(payload) })
      : await request("/api/custom-prompts", { method: "POST", body: JSON.stringify(payload) });
    if (!selectionHas(activeSection, item.id)) toggleSelection(activeSection, item.id, true);
    ui.customDialog.close();
    await loadCustomGroups();
    await loadPool();
    toast(editingCustom ? "自定义项已更新" : "自定义项已加入随机池");
  } catch (error) {
    toast(error.message);
  }
}
async function deleteCustomItem() {
  if (!editingCustom || !confirm("删除这个自定义项？")) return;
  try {
    await request(`/api/custom-prompts/${editingCustom.id}`, { method: "DELETE" });
    const selection = draft.pools[activeSection];
    selection.ids = selection.ids.filter((id) => id !== editingCustom.id);
    selection.excluded_ids = selection.excluded_ids.filter((id) => id !== editingCustom.id);
    ui.customDialog.close();
    await loadPool();
    renderDimensions();
    updatePoolOverview();
    schedulePersist();
    toast("自定义项已删除");
  } catch (error) {
    toast(error.message);
  }
}

function openCustomGroupDialog(group = null) {
  editingCustomGroup = group;
  ui.customGroupId.value = group?.id || "";
  ui.customGroupName.value = group?.name || "";
  ui.customGroupDialogTitle.textContent = group
    ? group.kind === "group"
      ? "编辑自定义分组"
      : "编辑导入大项"
    : "新建自定义分组";
  ui.deleteCustomGroup.hidden = !group;
  ui.customGroupDialog.showModal();
}
async function saveCustomGroup(event) {
  event.preventDefault();
  const id = ui.customGroupId.value;
  try {
    const payload = await request(
      id ? `/api/custom-groups/${activeSection}/${encodeURIComponent(id)}` : `/api/custom-groups/${activeSection}`,
      { method: id ? "PUT" : "POST", body: JSON.stringify({ name: ui.customGroupName.value }) },
    );
    customGroups = payload.groups || [];
    ui.customGroupDialog.close();
    renderPoolSidebar();
    toast(id ? "自定义分组已更新" : "自定义分组已创建");
  } catch (error) {
    toast(error.message);
  }
}
function removeCustomGroup() {
  if (editingCustomGroup) openDeleteGroupDialog("custom", editingCustomGroup);
}

function selectedImportGroupIds() {
  return [...ui.importTargetGroups.querySelectorAll("input:checked")].map((input) => input.value);
}
function selectedImportGroupNames() {
  const selected = new Set(selectedImportGroupIds());
  return customGroups.filter((group) => selected.has(group.id)).map((group) => customGroupPath(group));
}
function renderImportTargetGroups() {
  const leafGroups = customGroups.filter((group) => group.kind === "group");
  if (!leafGroups.length) {
    ui.importTargetGroups.innerHTML = '<div class="inline-empty">当前池暂无自定义分组，请先在池侧栏新建。</div>';
    return;
  }
  ui.importTargetGroups.replaceChildren(
    ...leafGroups.map((group) => {
      const label = document.createElement("label");
      label.className = "favorite-group-check";
      label.title = customGroupPath(group);
      label.innerHTML = `<input type="checkbox" value="${escapeHtml(group.id)}"><span>${escapeHtml(customGroupPath(group))}</span><small>${group.count || 0} 项</small>`;
      label.querySelector("input").addEventListener("change", () => {
        if (importPreview) renderImportPreview();
      });
      return label;
    }),
  );
}
function openImportDialog() {
  importPreview = null;
  const label = SECTION_META[activeSection].label;
  ui.importDialogTitle.textContent = `${label}池批量导入`;
  ui.importJsonTemplate.href = `/api/custom-prompts/templates/${activeSection}/json`;
  ui.importJsonTemplate.textContent = `${label} JSON 模板`;
  ui.importCsvTemplate.href = `/api/custom-prompts/templates/${activeSection}/csv`;
  ui.importCsvTemplate.textContent = `${label} CSV 模板`;
  ui.importFile.value = "";
  ui.importBundleName.value = "";
  ui.importHint.textContent = `仅导入${label}池条目；选择文件后会先校验，不会立即写入。`;
  ui.importSummary.hidden = true;
  ui.importRows.replaceChildren();
  ui.commitImport.disabled = true;
  renderImportTargetGroups();
  ui.importDialog.showModal();
}
async function previewImportFile() {
  const file = ui.importFile.files?.[0];
  if (!file) return;
  const format = file.name.toLowerCase().endsWith(".csv")
    ? "csv"
    : file.name.toLowerCase().endsWith(".json")
      ? "json"
      : "";
  if (!format) {
    toast("只支持 JSON 或 CSV 文件");
    return;
  }
  ui.importBundleName.value = file.name.replace(/\.[^.]+$/, "").trim();
  ui.importHint.textContent = `正在校验 ${file.name}`;
  try {
    importPreview = await request("/api/custom-prompts/import/preview", {
      method: "POST",
      body: JSON.stringify({
        format,
        content: await file.text(),
        section: activeSection,
        bundleName: ui.importBundleName.value,
      }),
    });
    importPreview.filename = file.name;
    renderImportPreview();
  } catch (error) {
    importPreview = null;
    ui.commitImport.disabled = true;
    ui.importHint.textContent = error.message;
    toast(error.message);
  }
}
function renderImportPreview() {
  const summary = importPreview.summary || {};
  ui.importHint.textContent = `${importPreview.filename} · 已完成校验`;
  ui.importSummary.hidden = false;
  ui.importSummary.innerHTML = `<span>新增 ${summary.new || 0}</span><span>冲突 ${summary.conflict || 0}</span><span>错误 ${summary.error || 0}</span>`;
  const labels = { new: "新增", conflict: "冲突", error: "错误" };
  ui.importRows.replaceChildren(
    ...importPreview.rows.map((row, index) => {
      const element = document.createElement("div");
      element.className = "import-row";
      element.dataset.status = row.status;
      const title = row.item?.title || "无法读取";
      const embeddedGroups = row.groups?.length ? row.groups : ["未分组"];
      const bundleName = ui.importBundleName.value.trim() || "未命名大项";
      const importPaths = embeddedGroups.map((name) => `${bundleName} / ${name}`);
      const targetGroups = selectedImportGroupNames();
      const detail = row.error || (row.action === "skip" ? "不导入" : [...importPaths, ...targetGroups].join("、"));
      element.innerHTML = `<span>#${row.row}</span><span class="import-status">${labels[row.status]}</span><strong title="${escapeHtml(title)}">${escapeHtml(title)}</strong><small title="${escapeHtml(detail)}">${escapeHtml(detail)}</small><select aria-label="导入操作" ${row.status === "error" ? "disabled" : ""}>${row.status === "new" ? '<option value="create">导入</option><option value="skip">跳过</option>' : row.status === "conflict" ? '<option value="skip">跳过</option><option value="overwrite">覆盖</option>' : '<option value="skip">跳过</option>'}</select>`;
      const select = element.querySelector("select");
      select.value = row.action;
      select.addEventListener("change", () => {
        importPreview.rows[index].action = select.value;
        renderImportPreview();
      });
      return element;
    }),
  );
  ui.commitImport.disabled =
    !ui.importBundleName.value.trim() ||
    !importPreview.rows.some((row) => row.status !== "error" && row.action !== "skip");
}
async function commitCustomImport() {
  if (!importPreview) return;
  ui.commitImport.disabled = true;
  try {
    const result = await request("/api/custom-prompts/import", {
      method: "POST",
      body: JSON.stringify({
        rows: importPreview.rows,
        section: activeSection,
        targetGroupIds: selectedImportGroupIds(),
        bundleName: ui.importBundleName.value,
      }),
    });
    ui.importDialog.close();
    await loadCustomGroups();
    await loadPool();
    renderDimensions();
    toast(`${result.bundleName}：新增 ${result.imported}，更新 ${result.updated}，跳过 ${result.skipped}`);
  } catch (error) {
    ui.commitImport.disabled = false;
    toast(error.message);
  }
}

function ensureSelectValue(select, value) {
  if (!select || !value) return;
  if (![...select.options].some((option) => option.value === value)) select.add(new Option(value, value));
  select.value = value;
}
function populateSelect(select, values, selected) {
  select.replaceChildren(...values.map((value) => new Option(value, value)));
  ensureSelectValue(select, selected);
}
function populateResourceSelect(select, values, selected, emptyText) {
  const options = values.map((value) => new Option(value, value));
  if (selected && !values.includes(selected)) {
    const missing = new Option(`当前缺失 · ${selected}`, selected);
    missing.dataset.missing = "true";
    options.unshift(missing);
  }
  if (!options.length) options.push(new Option(emptyText, ""));
  select.replaceChildren(...options);
  select.value = selected && [...select.options].some((option) => option.value === selected) ? selected : "";
}
function modelLabel(value) {
  const filename = String(value || "未选择模型")
    .replaceAll("\\", "/")
    .split("/")
    .pop();
  return filename.replace(/\.(safetensors|ckpt|pth)$/i, "");
}
async function loadResources() {
  const selectedModel = ui.model_name.value || defaults?.model_name || "";
  const selectedUpscaler = ui.hires_model_name.value || defaults?.hires?.model_name || "";
  const selectedSampler = ui.sampler_name.value || defaults?.sampler_name || "";
  const selectedScheduler = ui.scheduler.value || defaults?.scheduler || "";
  const selectedSecondSampler = ui.second_sampler_name.value || defaults?.second_sampler?.sampler_name || selectedSampler;
  const selectedSecondScheduler = ui.second_scheduler.value || defaults?.second_sampler?.scheduler || selectedScheduler;
  resourcesLoaded = false;
  resourceError = "";
  ui.model_name.disabled = true;
  ui.hires_model_name.disabled = true;
  ui.sampler_name.disabled = true;
  ui.scheduler.disabled = true;
  ui.second_sampler_name.disabled = true;
  ui.second_scheduler.disabled = true;
  ui.model_name.replaceChildren(new Option("正在读取模型...", ""));
  ui.hires_model_name.replaceChildren(new Option("正在读取放大模型...", ""));
  ui.sampler_name.replaceChildren(new Option("正在读取 Sampler...", ""));
  ui.scheduler.replaceChildren(new Option("正在读取 Scheduler...", ""));
  ui.second_sampler_name.replaceChildren(new Option("正在读取 Sampler...", ""));
  ui.second_scheduler.replaceChildren(new Option("正在读取 Scheduler...", ""));
  updateRepairControls();
  try {
    const payload = await request("/api/resources");
    resources = {
      models: Array.isArray(payload.models) ? payload.models : [],
      upscale_models: Array.isArray(payload.upscale_models) ? payload.upscale_models : [],
      samplers: Array.isArray(payload.samplers) ? payload.samplers : [],
      schedulers: Array.isArray(payload.schedulers) ? payload.schedulers : [],
    };
    resourcesLoaded = true;
    populateResourceSelect(ui.model_name, resources.models, selectedModel, "没有可用主模型");
    populateResourceSelect(ui.hires_model_name, resources.upscale_models, selectedUpscaler, "没有可用放大模型");
    populateResourceSelect(ui.sampler_name, resources.samplers, selectedSampler, "没有可用 Sampler");
    populateResourceSelect(ui.scheduler, resources.schedulers, selectedScheduler, "没有可用 Scheduler");
    populateResourceSelect(ui.second_sampler_name, resources.samplers, selectedSecondSampler, "没有可用 Sampler");
    populateResourceSelect(ui.second_scheduler, resources.schedulers, selectedSecondScheduler, "没有可用 Scheduler");
    ui.model_name.disabled = resources.models.length === 0;
    ui.sampler_name.disabled = resources.samplers.length === 0;
    ui.scheduler.disabled = resources.schedulers.length === 0;
  } catch (error) {
    resources = { models: [], upscale_models: [], samplers: [], schedulers: [] };
    resourceError = `模型资源读取失败：${error.message}`;
    populateResourceSelect(ui.model_name, [], selectedModel, "模型资源离线");
    populateResourceSelect(ui.hires_model_name, [], selectedUpscaler, "放大模型资源离线");
    populateResourceSelect(ui.sampler_name, [], selectedSampler, "Sampler 资源离线");
    populateResourceSelect(ui.scheduler, [], selectedScheduler, "Scheduler 资源离线");
    populateResourceSelect(ui.second_sampler_name, [], selectedSecondSampler, "Sampler 资源离线");
    populateResourceSelect(ui.second_scheduler, [], selectedSecondScheduler, "Scheduler 资源离线");
    ui.model_name.disabled = true;
  }
  updateRepairControls();
}
function updateSecondSamplerControls() {
  const enabled = ui.second_sampler_enabled.checked;
  ui.secondSamplerDrawer.hidden = !enabled;
  for (const control of [
    ui.second_sampler_steps,
    ui.second_sampler_cfg,
    ui.second_sampler_name,
    ui.second_scheduler,
    ui.second_sampler_denoise,
  ]) control.disabled = !enabled || (control.tagName === "SELECT" && !resourcesLoaded);
}
function updateRepairControls() {
  const detailerCount = [ui.detailer_hand, ui.detailer_nsfw, ui.detailer_face, ui.detailer_eyes].filter(
    (input) => input.checked,
  ).length;
  ui.repairSummary.textContent = `${modelLabel(ui.model_name.value || defaults?.model_name)} · ${ui.hires_enabled.checked ? "高清开启" : "高清关闭"} · ${detailerCount} 项细修`;
  ui.hiresFields.classList.toggle("disabled", !ui.hires_enabled.checked);
  ui.hires_model_name.disabled = !ui.hires_enabled.checked || !resourcesLoaded;
  ui.hires_percent.disabled = !ui.hires_enabled.checked;
  updateSecondSamplerControls();
  const settings = readSettings();
  const warnings = [];
  if (resourceError) warnings.push(resourceError);
  if (resourcesLoaded && !resources.models.length) warnings.push("ComfyUI 当前没有可用主模型");
  if (resourcesLoaded && !resources.upscale_models.length) warnings.push("ComfyUI 当前没有可用放大模型");
  if (resourcesLoaded && !resources.samplers.length) warnings.push("ComfyUI 当前没有可用 Sampler");
  if (resourcesLoaded && !resources.schedulers.length) warnings.push("ComfyUI 当前没有可用 Scheduler");
  if (resourcesLoaded && !resources.models.includes(settings.model_name))
    warnings.push(`主模型不可用：${settings.model_name}`);
  if (resourcesLoaded && settings.hires.enabled && !resources.upscale_models.includes(settings.hires.model_name))
    warnings.push(`高清模型不可用：${settings.hires.model_name}`);
  if (resourcesLoaded && !resources.samplers.includes(settings.sampler_name))
    warnings.push(`Sampler 不可用：${settings.sampler_name}`);
  if (resourcesLoaded && !resources.schedulers.includes(settings.scheduler))
    warnings.push(`Scheduler 不可用：${settings.scheduler}`);
  if (resourcesLoaded && settings.second_sampler.enabled && !resources.samplers.includes(settings.second_sampler.sampler_name))
    warnings.push(`2ndSampler Sampler 不可用：${settings.second_sampler.sampler_name}`);
  if (resourcesLoaded && settings.second_sampler.enabled && !resources.schedulers.includes(settings.second_sampler.scheduler))
    warnings.push(`2ndSampler Scheduler 不可用：${settings.second_sampler.scheduler}`);
  const missingLoras = settings.loras.filter((item) => !loraItem(item.filename)).map((item) => item.filename);
  if (loraInventoryLoaded && missingLoras.length) warnings.push(`LoRA 不可用：${missingLoras.join("、")}`);
  ui.resourceWarning.hidden = warnings.length === 0;
  ui.resourceWarning.textContent = warnings.join("；");
}

const PRESET_SETTING_KEYS = [
  // 人物构成与角色细节:必须与后端 PRESET_SETTING_KEYS 及 DEFAULT_SETTINGS 对齐,
  // 否则 presetSnapshot() 会丢弃 female_count/male_count/character_detail,
  // 导致保存预设或载入预设时人物构成与角色细节模式无法还原。
  "female_count",
  "male_count",
  "character_detail",
  "model_name",
  "loras",
  "lora_managed_triggers",
  "hires",
  "detailers",
  "manual_artist",
  "quality_prompt",
  "extra_prompt",
  "negative_prompt",
  "width",
  "height",
  "steps",
  "cfg",
  "sampler_name",
  "scheduler",
  "cfg_zero_star",
  "second_sampler",
  // 提示词池:开关、抽取数量、固定提示词与随机池勾选条目。
  // 必须与后端 PRESET_SETTING_KEYS 及 DEFAULT_SETTINGS 保持一致,
  // 否则保存时会被 presetSnapshot() 丢弃,应用时无法回填 5 个池。
  "random_character",
  "random_clothing",
  "random_pose",
  "random_background",
  "random_expression",
  "random_character_count",
  "random_clothing_count",
  "random_pose_count",
  "random_background_count",
  "random_expression_count",
  "fixed_character",
  "fixed_clothing",
  "fixed_pose",
  "fixed_background",
  "fixed_expression",
  "pools",
];
function presetSnapshot() {
  const settings = readSettings();
  return Object.fromEntries(PRESET_SETTING_KEYS.map((key) => [key, clone(settings[key])]));
}
async function loadStylePresets() {
  try {
    const data = await request("/api/style-presets");
    stylePresets = data.items || [];
    // 后端已按 updated_at 倒序返回,这里再稳定排序一次,保证“全部”视图始终时间倒序。
    stylePresets.sort((a, b) => String(b.updated_at || "").localeCompare(String(a.updated_at || "")));
    presetAllTotal = stylePresets.length;
    renderStylePresets();
    renderPresetCollections();
  } catch (error) {
    toast(error.message);
  }
}
function setPresetFeedback(message = "", type = "error") {
  ui.presetError.textContent = message;
  ui.presetError.hidden = !message;
  ui.presetError.dataset.type = type;
}

// ---------- 预设库二级筛选胶囊栏 ----------
function presetCollectionIds(item) {
  return Array.isArray(item?.collection_ids) ? item.collection_ids.map(Number) : [];
}

function presetIsFavorite(item) {
  return presetCollectionIds(item).includes(DEFAULT_COLLECTION_ID);
}

// 工具函数:获取所有母文件夹(包括默认收藏)。
function presetParentCollections() {
  return presetCollections.filter((c) => c.parent_id == null);
}

// 工具函数:获取指定母文件夹下的所有子文件夹。
function presetSubCollections(parentId) {
  const pid = Number(parentId);
  if (!pid || pid <= 1) return [];
  return presetCollections.filter((c) => Number(c.parent_id) === pid);
}

// 当前筛选视图下的预设集合(不改变 stylePresets 的原始时间倒序)。
// 全部/收藏平铺展示;普通母类仅展示当前激活子文件夹的预设。
function visibleStylePresets() {
  const parentId = Number(currentPresetParentId) || 0;

  // 1. 全部视图:展示所有预设
  if (parentId === 0) {
    return stylePresets;
  }

  // 2. 默认收藏:展示所有打了星标的预设
  if (parentId === DEFAULT_COLLECTION_ID) {
    return stylePresets.filter((item) => presetIsFavorite(item));
  }

  // 3. 具体母分类:严格按照当前选中的子分类 ID 过滤
  const subId = Number(currentPresetSubId) || 0;
  if (subId <= 0) {
    return []; // 该母文件夹下暂无子分类或未选中子分类
  }
  return stylePresets.filter((item) => presetCollectionIds(item).includes(subId));
}

// 各分类计数:优先使用后端统计,缺失时按内存数据即时统计,保证徽标与卡片归属严格同步。
// 母文件夹的兜底统计需汇聚名下所有子文件夹的归属预设(去重),与后端 list_collections 口径一致。
function presetCollectionCount(collectionId) {
  const target = Number(collectionId) || 0;
  if (target === 0) return Math.max(0, Number(presetAllTotal) || stylePresets.length);
  const cached = presetCollections.find((item) => Number(item.id) === target);
  if (cached && Number.isFinite(Number(cached.count))) return Math.max(0, Number(cached.count));
  const subIds = presetSubCollections(target).map((item) => Number(item.id));
  if (subIds.length) {
    return stylePresets.filter((item) =>
      presetCollectionIds(item).some((id) => subIds.includes(id)),
    ).length;
  }
  return stylePresets.filter((item) => presetCollectionIds(item).includes(target)).length;
}

// 就地刷新胶囊徽标,不重建 DOM,避免点击星标时胶囊栏闪烁。
// 母类与子类胶囊栏都要查询:同一分类 ID 只可能出现在其中一栏。
function paintPresetCollectionBadge(collectionId, count) {
  const selector = `.collection-pill[data-collection-id="${Number(collectionId)}"] .pill-badge`;
  for (const bar of [ui.presetCollectionsBar, ui.presetSubCollectionsBar]) {
    const pill = bar?.querySelector(selector);
    if (pill) pill.textContent = String(Math.max(0, Number(count) || 0));
  }
}

function adjustPresetCollectionCount(collectionId, delta) {
  const target = Number(collectionId);
  if (!Number.isFinite(target) || !delta) return;
  const cached = presetCollections.find((item) => Number(item.id) === target);
  if (cached) cached.count = Math.max(0, Number(cached.count || 0) + delta);
  paintPresetCollectionBadge(target, presetCollectionCount(target));
}

// 通用胶囊创建工厂(支持母类/子类):isSub 决定点击路由与重命名/删除的 type。
function createPresetCollectionPill({ id, icon, name, count, active, deletable, isSub = false }) {
  const pill = document.createElement("button");
  pill.type = "button";
  pill.className = "collection-pill";
  if (Number(id) === 0) pill.classList.add("pill-all");
  pill.dataset.collectionId = String(id);
  pill.setAttribute("aria-pressed", active ? "true" : "false");
  if (active) pill.classList.add("active");
  const iconSpan = document.createElement("span");
  iconSpan.className = "collection-pill-icon";
  iconSpan.setAttribute("aria-hidden", "true");
  iconSpan.textContent = icon;
  const nameSpan = document.createElement("span");
  nameSpan.className = "collection-pill-name";
  nameSpan.textContent = name;
  const badge = document.createElement("span");
  badge.className = "pill-badge";
  badge.textContent = String(count);
  pill.append(iconSpan, nameSpan, badge);
  const pillType = isSub ? "preset_sub" : "preset";
  pill.addEventListener("click", () => {
    if (isSub) selectPresetSubCollection(id);
    else selectPresetParentCollection(id);
  });
  if (deletable) {
    // 双击胶囊快速重命名(快捷操作)。
    pill.addEventListener("dblclick", (event) => {
      event.stopPropagation();
      event.preventDefault();
      openCollectionRenameDialog(pillType, id, name);
    });

    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.className = "collection-pill-edit";
    editBtn.title = `重命名“${name}”`;
    editBtn.setAttribute("aria-label", `重命名 ${name}`);
    editBtn.textContent = "✎";
    editBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      event.preventDefault();
      openCollectionRenameDialog(pillType, id, name);
    });
    pill.append(editBtn);

    const menu = document.createElement("button");
    menu.type = "button";
    menu.className = "collection-pill-menu";
    menu.title = `删除${isSub ? "子文件夹" : "分类"}“${name}”`;
    menu.setAttribute("aria-label", `删除${isSub ? "子文件夹" : "分类"} ${name}`);
    menu.textContent = "···";
    menu.addEventListener("click", (event) => {
      event.stopPropagation();
      event.preventDefault();
      openCollectionDeleteDialog(pillType, id, name);
    });
    pill.append(menu);
  }
  return pill;
}

// ---------- 渲染母文件夹胶囊栏 ----------
function renderPresetCollections() {
  if (!ui.presetCollectionsBar) return;
  const pills = [
    createPresetCollectionPill({
      id: 0,
      icon: "▦",
      name: "全部",
      count: presetCollectionCount(0),
      active: Number(currentPresetParentId) === 0,
      deletable: false,
      isSub: false,
    }),
  ];
  // 仅渲染母文件夹:子文件夹由 renderPresetSubCollections 单独承接。
  const parents = presetParentCollections().sort((a, b) => {
    const defaultDelta = Number(Boolean(b.is_default)) - Number(Boolean(a.is_default));
    if (defaultDelta) return defaultDelta;
    return Number(a.id) - Number(b.id);
  });
  for (const collection of parents) {
    const id = Number(collection.id);
    pills.push(
      createPresetCollectionPill({
        id,
        icon: collection.is_default ? "★" : "📁",
        name: String(collection.name || "未命名"),
        count: presetCollectionCount(id),
        active: Number(currentPresetParentId) === id,
        deletable: !collection.is_default,
        isSub: false,
      }),
    );
  }
  // 新建入口已改为右侧常驻静态按钮(#btnPresetAddCollection),不再随胶囊列表滚动。
  ui.presetCollectionsBar.replaceChildren(...pills);
  syncCollectionsOverflow(ui.presetCollectionsBar);
}

// ---------- 渲染子文件夹胶囊栏 ----------
function renderPresetSubCollections() {
  const wrapper = ui.presetSubCollectionsBarWrapper;
  const bar = ui.presetSubCollectionsBar;
  if (!wrapper || !bar) return;

  const parentId = Number(currentPresetParentId) || 0;

  // 业务边界1:选中“全部”或“默认收藏”时,子分类栏收起隐藏。
  if (parentId <= 1) {
    wrapper.hidden = true;
    bar.replaceChildren();
    return;
  }

  // 选中普通母分类时展开显示。
  wrapper.hidden = false;
  const subs = presetSubCollections(parentId).sort((a, b) => Number(a.id) - Number(b.id));

  if (!subs.length) {
    const emptySpan = document.createElement("span");
    emptySpan.className = "sub-collections-empty-hint";
    emptySpan.textContent = "暂无子分类，请点击右侧“＋”创建";
    bar.replaceChildren(emptySpan);
    syncCollectionsOverflow(bar);
    return;
  }

  const pills = subs.map((sub) => {
    const id = Number(sub.id);
    return createPresetCollectionPill({
      id,
      icon: "🗂",
      name: String(sub.name || "未命名"),
      count: presetCollectionCount(id),
      active: Number(currentPresetSubId) === id,
      deletable: true,
      isSub: true,
    });
  });

  bar.replaceChildren(...pills);
  syncCollectionsOverflow(bar);
}

async function loadPresetCollections() {
  const requestId = ++presetCollectionsRequest;
  try {
    const payload = await request("/api/style-presets/collections");
    if (requestId !== presetCollectionsRequest) return;
    presetCollections = Array.isArray(payload?.collections) ? payload.collections : [];
    const allTotal = Number(payload?.all_total);
    if (Number.isFinite(allTotal)) presetAllTotal = Math.max(0, allTotal);
    // 当前激活母分类若已被删除,自动回落到“全部”。
    if (
      Number(currentPresetParentId) !== 0 &&
      !presetCollections.some((item) => Number(item.id) === Number(currentPresetParentId))
    ) {
      currentPresetParentId = 0;
      currentPresetSubId = 0;
    }
    // 当前激活子分类若已被删除或不再属于该母类,回退至同级首个子分类。
    if (Number(currentPresetParentId) > 1) {
      const subs = presetSubCollections(currentPresetParentId);
      if (!subs.some((item) => Number(item.id) === Number(currentPresetSubId))) {
        currentPresetSubId = subs.length > 0 ? Number(subs[0].id) : 0;
      }
    } else {
      currentPresetSubId = 0;
    }
    renderPresetCollections();
    renderPresetSubCollections();
    renderStylePresets();
  } catch (error) {
    if (requestId !== presetCollectionsRequest) return;
    toast(error.message);
  }
}

// ---------- 核心联动逻辑:选择母文件夹 ----------
function selectPresetParentCollection(parentId) {
  const target = Number(parentId) || 0;
  if (target === Number(currentPresetParentId)) return;

  currentPresetParentId = target;
  presetPage = 1; // 切换分类重置页码

  if (target <= 1) {
    currentPresetSubId = 0;
  } else {
    // 关键联动:自动选中该母分类下的首个子分类。
    const subs = presetSubCollections(target);
    currentPresetSubId = subs.length > 0 ? Number(subs[0].id) : 0;
  }

  renderPresetCollections();
  renderPresetSubCollections();
  renderStylePresets();
}

// ---------- 核心联动逻辑:选择子文件夹 ----------
function selectPresetSubCollection(subId) {
  const target = Number(subId) || 0;
  if (target === Number(currentPresetSubId)) return;

  currentPresetSubId = target;
  presetPage = 1; // 切换分类重置页码

  renderPresetSubCollections();
  renderStylePresets();
}

// 预设库新建/删除统一走 #collectionCreateDialog / #collectionDeleteDialog 模态弹窗,
// 具体提交逻辑见 submitCollectionCreate / submitCollectionDelete。

// ---------- 预设星标:乐观更新 + 弹跳微动效(对齐作品库 toggleDefaultFavorite) ----------
function paintPresetFavoriteStar(star, favorite) {
  star.dataset.favorite = favorite ? "true" : "false";
  star.setAttribute("aria-pressed", favorite ? "true" : "false");
  star.title = favorite ? "取消收藏" : "收藏";
}

async function togglePresetDefaultFavorite(item, star) {
  const previous = presetIsFavorite(item);
  const optimistic = !previous;
  // 乐观更新:先点亮/熄灭并播放微弹跳,卡片保持原地不动。
  paintPresetFavoriteStar(star, optimistic);
  star.classList.remove("is-popping");
  void star.offsetWidth;
  star.classList.add("is-popping");
  if (optimistic !== previous) adjustPresetCollectionCount(DEFAULT_COLLECTION_ID, optimistic ? 1 : -1);
  try {
    const result = await request(
      `/api/style-presets/${encodeURIComponent(item.id)}/toggle-default-favorite`,
      { method: "POST" },
    );
    const favorite = Boolean(result?.is_favorite);
    const ids = Array.isArray(result?.collection_ids) ? result.collection_ids.map(Number) : [];
    paintPresetFavoriteStar(star, favorite);
    item.favorite = favorite;
    item.collection_ids = ids;
    // 以服务端结果为准校正徽标(乐观增量与真实结果不一致时回补差值)。
    if (favorite !== optimistic) {
      adjustPresetCollectionCount(DEFAULT_COLLECTION_ID, favorite ? 1 : -1);
    }
  } catch (error) {
    // 失败回滚:恢复星标与徽标,并提示原因。
    paintPresetFavoriteStar(star, previous);
    if (optimistic !== previous) adjustPresetCollectionCount(DEFAULT_COLLECTION_ID, previous ? 1 : -1);
    toast(error.message);
  }
}

function renderStylePresets() {
  const items = visibleStylePresets();
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / PRESET_PAGE_SIZE));
  // 防止删除/切换分类后当前页溢出。
  if (presetPage > totalPages) presetPage = totalPages;
  if (presetPage < 1) presetPage = 1;

  ui.presetSummary.textContent = `${total} 个预设`;
  ui.presetsCount.textContent = String(Math.max(0, Number(presetAllTotal) || stylePresets.length));
  ui.presetEmpty.hidden = total > 0;

  // 更新分页栏显示与按钮可用状态。
  if (ui.presetPageLabel) ui.presetPageLabel.textContent = `${presetPage} / ${totalPages}`;
  if (ui.presetPrevPage) ui.presetPrevPage.disabled = presetPage <= 1;
  if (ui.presetNextPage) ui.presetNextPage.disabled = presetPage >= totalPages;

  // 取当前页切片数据。
  const startIndex = (presetPage - 1) * PRESET_PAGE_SIZE;
  const pageItems = items.slice(startIndex, startIndex + PRESET_PAGE_SIZE);

  ui.presetGrid.replaceChildren(
    ...pageItems.map((item) => {
      const card = document.createElement("div");
      card.className = "preset-card";
      card.dataset.presetId = item.id;
      const thumbUrl = presetThumbnailUrl(item);
      const thumbMarkup = item.thumbnail_url
        ? `<img class="preset-thumb" src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(item.name)}" loading="lazy">`
        : `<span class="preset-thumb-placeholder" aria-hidden="true">★</span>`;
      const favorite = presetIsFavorite(item);
      card.innerHTML = `
        <button type="button" class="batch-check" role="checkbox" aria-checked="false" aria-label="选择预设 ${escapeHtml(item.name)}" tabindex="-1"></button>
        <div class="preset-thumb-wrapper">
          ${thumbMarkup}
          <div class="preset-hover-overlay">
            <button class="action-btn btn-load" type="button" title="一键载入">⚡ 载入</button>
            <button class="action-btn btn-overwrite" type="button" title="用当前设置覆盖">⟳ 覆盖</button>
            <button class="action-btn btn-rename" type="button" title="重命名">✎ 改名</button>
            <button class="action-btn btn-collection" type="button" title="归类到收藏夹">📁 归类</button>
            <button class="action-btn btn-delete" type="button" title="删除">🗑 删除</button>
          </div>
        </div>
        <div class="preset-info">
          <span class="preset-name" title="${escapeHtml(item.name)}">${escapeHtml(item.name)}</span>
          <button class="preset-favorite-icon" type="button" data-favorite="${favorite ? "true" : "false"}" aria-pressed="${favorite ? "true" : "false"}" title="${favorite ? "取消收藏" : "收藏"}" aria-label="${favorite ? "取消收藏" : "收藏"}">★</button>
        </div>`;
      card.querySelector(".btn-load").addEventListener("click", () => loadStylePreset(item));
      card.querySelector(".btn-overwrite").addEventListener("click", () => openPresetOverwriteDialog(item));
      card.querySelector(".btn-rename").addEventListener("click", () => openPresetRenameDialog(item));
      card.querySelector(".btn-collection").addEventListener("click", () => openPresetCollectionsDialog(item));
      card.querySelector(".btn-delete").addEventListener("click", () => openPresetDeleteDialog(item));
      const presetFavoriteIcon = card.querySelector(".preset-favorite-icon");
      presetFavoriteIcon.addEventListener("click", (event) => {
        event.stopPropagation();
        togglePresetDefaultFavorite(item, event.currentTarget);
      });
      // 指针按下阶段即拦截,避免事件穿透到卡片触发批量勾选等逻辑。
      presetFavoriteIcon.addEventListener("pointerdown", (event) => {
        event.stopPropagation();
      });
      // 批量模式下点击卡片任意位置 = 切换勾选,绝不触发载入/弹窗等常规操作。
      card.addEventListener("click", (event) => {
        if (!isPresetBatchMode) return;
        event.preventDefault();
        event.stopPropagation();
        togglePresetBatchSelection(item.id, { shiftKey: event.shiftKey });
      });
      // 复选框是独立控件:阻止冒泡,避免与卡片点击重复触发。
      card.querySelector(".batch-check").addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        togglePresetBatchSelection(item.id, { shiftKey: event.shiftKey });
      });
      return card;
    }),
  );
  // 翻页/重绘后重新同步批量视觉状态:选择集合跨页保留,但只高亮当前页可见项。
  ui.presetGrid.classList.toggle("is-batch-mode", isPresetBatchMode);
  if (isPresetBatchMode) paintPresetBatchSelection();
}

// ---------- 预设库批量管理:选择逻辑 ----------
function presetBatchCardElements() {
  if (!ui.presetGrid) return [];
  return [...ui.presetGrid.querySelectorAll(".preset-card")];
}

// 当前页可见预设 ID 顺序(与 DOM 顺序一致,保证 Shift 区间语义正确)。
function presetBatchPageIds() {
  return presetBatchCardElements()
    .map((element) => String(element.dataset.presetId || ""))
    .filter((value) => value);
}

function paintPresetBatchCard(card, presetId) {
  if (!card) return;
  const selected = selectedPresetBatchIds.has(String(presetId));
  card.classList.toggle("is-selected", selected);
  const check = card.querySelector(".batch-check");
  if (check) {
    check.setAttribute("aria-checked", selected ? "true" : "false");
    check.title = selected ? "取消选择" : "选择此预设";
  }
}

// 就地刷新当前页卡片的选中态,不重建 DOM(避免缩略图重新加载)。
function paintPresetBatchSelection() {
  for (const card of presetBatchCardElements()) {
    paintPresetBatchCard(card, card.dataset.presetId);
  }
  updatePresetBatchActionBar();
}

// 底部操作条在预设库模式下复用:计数、全选文案与按钮可用性均按预设集合计算。
function updatePresetBatchActionBar() {
  const count = selectedPresetBatchIds.size;
  if (ui.batchSelectedCount) ui.batchSelectedCount.textContent = String(count);
  const pageIds = presetBatchPageIds();
  const allSelected =
    pageIds.length > 0 && pageIds.every((id) => selectedPresetBatchIds.has(id));
  if (ui.batchSelectAll) {
    ui.batchSelectAll.textContent = allSelected ? "取消全选" : "全选本页";
    ui.batchSelectAll.disabled = pageIds.length === 0;
    ui.batchSelectAll.setAttribute("aria-pressed", allSelected ? "true" : "false");
  }
  const empty = count === 0;
  for (const button of [ui.batchFavorite, ui.batchDelete]) {
    if (button) button.disabled = empty || presetBatchBusy;
  }
  if (ui.batchClearSelection) ui.batchClearSelection.disabled = empty || presetBatchBusy;
  if (ui.batchExit) ui.batchExit.disabled = presetBatchBusy;
  if (ui.batchActionBar) ui.batchActionBar.classList.toggle("is-busy", presetBatchBusy);
}

function setPresetBatchMode(enabled) {
  const next = Boolean(enabled);
  if (next === isPresetBatchMode) return;
  isPresetBatchMode = next;
  document.body.classList.toggle("is-batch-mode", isPresetBatchMode);
  // 生图控制台与批量操作条互斥:与作品库批量模式共用同一收起类名。
  const deck = ui.commandDeck || document.querySelector(".command-deck");
  if (deck) {
    deck.classList.toggle("is-batch-hidden", isPresetBatchMode);
    deck.setAttribute("aria-hidden", String(isPresetBatchMode));
  }
  if (ui.presetGrid) ui.presetGrid.classList.toggle("is-batch-mode", isPresetBatchMode);
  if (ui.btnTogglePresetBatchMode) {
    ui.btnTogglePresetBatchMode.setAttribute("aria-pressed", String(isPresetBatchMode));
    ui.btnTogglePresetBatchMode.title = isPresetBatchMode ? "退出批量管理" : "批量管理预设";
    const label = ui.btnTogglePresetBatchMode.querySelector("span");
    if (label) label.textContent = isPresetBatchMode ? "退出批量" : "批量管理";
  }
  if (isPresetBatchMode) {
    // 复用底部操作条,但预设库没有导出能力,必须隐藏导出按钮。
    if (ui.batchExport) ui.batchExport.hidden = true;
    showBatchActionBar();
    paintPresetBatchSelection();
  } else {
    selectedPresetBatchIds.clear();
    lastPresetBatchAnchorId = null;
    // 批量弹窗若仍打开,一并复位关闭,避免上下文悬挂。
    if (presetBatchCollectionsContext && ui.presetCollectionsDialog?.open) {
      closePresetBatchCollectionsDialog();
    }
    if (presetBatchDeleteContext && ui.presetDeleteDialog?.open) {
      closePresetBatchDeleteDialog();
    }
    paintPresetBatchSelection();
    hideBatchActionBar();
    if (ui.batchExport) ui.batchExport.hidden = false;
  }
}

function togglePresetBatchSelection(presetId, { shiftKey = false } = {}) {
  const target = String(presetId || "");
  if (!target) return;
  if (!isPresetBatchMode) setPresetBatchMode(true);

  if (shiftKey && lastPresetBatchAnchorId !== null) {
    const pageIds = presetBatchPageIds();
    const from = pageIds.indexOf(lastPresetBatchAnchorId);
    const to = pageIds.indexOf(target);
    if (from >= 0 && to >= 0) {
      // 区间连选:以目标项当前状态为准,整段统一为“选中”或“取消”。
      const shouldSelect = !selectedPresetBatchIds.has(target);
      const [start, end] = from <= to ? [from, to] : [to, from];
      for (let index = start; index <= end; index += 1) {
        if (shouldSelect) selectedPresetBatchIds.add(pageIds[index]);
        else selectedPresetBatchIds.delete(pageIds[index]);
      }
      lastPresetBatchAnchorId = target;
      paintPresetBatchSelection();
      return;
    }
  }

  if (selectedPresetBatchIds.has(target)) selectedPresetBatchIds.delete(target);
  else selectedPresetBatchIds.add(target);
  lastPresetBatchAnchorId = target;
  paintPresetBatchSelection();
}

function selectAllPresetBatchPage() {
  const pageIds = presetBatchPageIds();
  if (!pageIds.length) return;
  const allSelected = pageIds.every((id) => selectedPresetBatchIds.has(id));
  for (const id of pageIds) {
    if (allSelected) selectedPresetBatchIds.delete(id);
    else selectedPresetBatchIds.add(id);
  }
  lastPresetBatchAnchorId = allSelected ? null : pageIds[pageIds.length - 1];
  paintPresetBatchSelection();
}

function clearPresetBatchSelection() {
  selectedPresetBatchIds.clear();
  lastPresetBatchAnchorId = null;
  paintPresetBatchSelection();
}

// 批量请求统一入口:锁定操作条、串行执行、结束后刷新选择态。
async function runPresetBatchTask(task, { onError } = {}) {
  if (presetBatchBusy) return;
  presetBatchBusy = true;
  updatePresetBatchActionBar();
  try {
    await task();
  } catch (error) {
    const message = error?.message || "批量操作失败";
    if (typeof onError === "function") onError(message);
    else toast(message);
  } finally {
    presetBatchBusy = false;
    updatePresetBatchActionBar();
  }
}

// ---------- 预设批量归类:复用 #presetCollectionsDialog ----------
function presetBatchSelectedItems() {
  return stylePresets.filter((item) => selectedPresetBatchIds.has(String(item.id)));
}

function openPresetBatchCollectionsDialog() {
  const items = presetBatchSelectedItems();
  if (!items.length) {
    toast("请先选择要归类的预设");
    return;
  }
  presetBatchCollectionsContext = { ids: items.map((item) => String(item.id)) };
  setPresetCollectionsError("");
  // 交集语义:仅当所有选中预设都已归属某分类时才默认勾选,避免误覆盖。
  const intersection = items.reduce((acc, item) => {
    const ids = new Set(presetCollectionIds(item));
    return acc === null ? ids : new Set([...acc].filter((id) => ids.has(id)));
  }, null);
  if (ui.presetCollectionsTitle) ui.presetCollectionsTitle.textContent = "批量归类风格预设";
  if (ui.presetCollectionsSummary) {
    ui.presetCollectionsSummary.textContent = `已选 ${items.length} 个预设，勾选要归入的子文件夹（保存后将整体覆盖这些预设的归属）：`;
  }
  renderPresetCollectionsChecklist([...(intersection || [])]);
  ui.presetCollectionsDialog.showModal();
}

function closePresetBatchCollectionsDialog() {
  presetBatchCollectionsContext = null;
  if (ui.presetCollectionsSummary) {
    ui.presetCollectionsSummary.textContent = "";
  }
  if (ui.presetCollectionsTitle) ui.presetCollectionsTitle.textContent = "归类预设";
  ui.presetCollectionsDialog?.close();
}

async function submitPresetBatchCollections() {
  const context = presetBatchCollectionsContext;
  if (!context || presetCollectionsSaving) return;
  const collectionIds = checkedPresetCollectionIds();
  // 全部取消勾选时改用 remove 清空所有分类,语义等价于“移出全部收藏夹”。
  const clearing = collectionIds.length === 0;
  presetCollectionsSaving = true;
  const submitButton = ui.presetCollectionsForm?.querySelector('button[type="submit"]');
  if (submitButton) submitButton.disabled = true;
  setPresetCollectionsError("");
  try {
    const result = await request("/api/style-presets/batch-collections", {
      method: "POST",
      body: JSON.stringify({
        preset_ids: context.ids,
        collection_ids: clearing
          ? presetCollections.map((item) => Number(item.id)).filter((id) => id > 0)
          : collectionIds,
        mode: clearing ? "remove" : "set",
      }),
    });
    const updated = new Set(
      (Array.isArray(result?.updated) ? result.updated : context.ids).map(String),
    );
    // 本地内存同步:set 模式整体覆盖,remove 模式逐个剔除。
    for (const item of stylePresets) {
      if (!updated.has(String(item.id))) continue;
      const current = presetCollectionIds(item);
      const next = clearing
        ? current.filter((id) => !collectionIds.includes(id) && !presetCollections.some((c) => Number(c.id) === id))
        : [...collectionIds];
      item.collection_ids = [...new Set(next)].sort((a, b) => a - b);
      item.favorite = item.collection_ids.includes(DEFAULT_COLLECTION_ID);
    }
    closePresetBatchCollectionsDialog();
    // 归类会改变各分类归属,重新拉取统计以保证徽标与卡片严格同步。
    await loadPresetCollections();
    paintPresetBatchSelection();
    toast(
      clearing
        ? `已将 ${updated.size} 个预设移出全部分类`
        : `已更新 ${updated.size} 个预设的分类归属`,
    );
  } catch (error) {
    setPresetCollectionsError(error.message || "批量归类失败");
  } finally {
    presetCollectionsSaving = false;
    if (submitButton) submitButton.disabled = false;
  }
}

// ---------- 预设批量删除:复用 #presetDeleteDialog ----------
function openPresetBatchDeleteDialog() {
  const ids = [...selectedPresetBatchIds];
  if (!ids.length) {
    toast("请先选择要删除的预设");
    return;
  }
  presetBatchDeleteContext = { ids };
  if (ui.presetDeleteSummary) {
    ui.presetDeleteSummary.textContent = `已选 ${ids.length} 项预设，删除后将同步移除磁盘封面缩略图，此操作无法撤销。`;
  }
  const title = ui.presetDeleteDialog?.querySelector(".dialog-heading h2");
  if (title) title.textContent = `批量删除 ${ids.length} 项预设`;
  setPresetDialogError(ui.presetDeleteError);
  if (ui.confirmPresetDelete) {
    ui.confirmPresetDelete.disabled = false;
    ui.confirmPresetDelete.textContent = "确认删除";
  }
  ui.presetDeleteDialog.showModal();
}

function closePresetBatchDeleteDialog() {
  presetBatchDeleteContext = null;
  if (ui.presetDeleteSummary) ui.presetDeleteSummary.textContent = "";
  const title = ui.presetDeleteDialog?.querySelector(".dialog-heading h2");
  if (title) title.textContent = "删除预设";
  ui.presetDeleteDialog?.close();
}

async function submitPresetBatchDelete() {
  const context = presetBatchDeleteContext;
  if (!context || ui.confirmPresetDelete?.disabled) return;
  const ids = [...context.ids];
  if (ui.confirmPresetDelete) {
    ui.confirmPresetDelete.disabled = true;
    ui.confirmPresetDelete.textContent = "正在删除...";
  }
  setPresetDialogError(ui.presetDeleteError);
  await runPresetBatchTask(
    async () => {
      const result = await request("/api/style-presets/batch-delete", {
        method: "POST",
        body: JSON.stringify({ preset_ids: ids }),
      });
      const deleted = Number(result?.deleted ?? ids.length);
      const removed = new Set(ids.map(String));
      for (const id of removed) selectedPresetBatchIds.delete(id);
      lastPresetBatchAnchorId = null;
      stylePresets = stylePresets.filter((preset) => !removed.has(String(preset.id)));
      presetAllTotal = stylePresets.length;
      closePresetBatchDeleteDialog();
      // 删除后当前页可能已空:renderStylePresets 内部会自动回退页码。
      await loadPresetCollections();
      renderStylePresets();
      paintPresetBatchSelection();
      toast(`已删除 ${deleted} 个预设`);
    },
    {
      onError: (message) => {
        setPresetDialogError(ui.presetDeleteError, message);
      },
    },
  );
  if (ui.confirmPresetDelete) {
    ui.confirmPresetDelete.disabled = false;
    ui.confirmPresetDelete.textContent = "确认删除";
  }
}

// ---------- 一键载入:全量恢复工作台状态 ----------
function loadStylePreset(item) {
  const settings = item.settings || {};
  // 全量覆盖:以预设 settings 为基准,补齐运行期字段(count)后整体应用,
  // 确保提示词池、LoRA、画师、主模型、分辨率、步数、CFG、采样器等全部精确还原。
  applySettings({ ...clone(settings), count: Number(ui.count.value) || 1 });
  schedulePersist();
  toast(`已载入预设：【${item.name}】`);
}

// ---------- 覆盖更新:PUT + 可选同步缩略图 ----------
let presetOverwriteTarget = null;
function openPresetOverwriteDialog(item) {
  presetOverwriteTarget = item;
  ui.presetOverwriteSummary.textContent = `是否使用当前工作台设置覆盖预设【${item.name}】？`;
  ui.presetOverwriteThumb.checked = false;
  setPresetDialogError(ui.presetOverwriteError);
  ui.presetOverwriteDialog.showModal();
}
async function submitPresetOverwrite() {
  const item = presetOverwriteTarget;
  if (!item) return;
  const syncThumb = ui.presetOverwriteThumb.checked;
  // 同步缩略图时必须取全库最新作品,而非当前分页/筛选结果的首条。
  const latest = syncThumb ? await fetchLatestHistoryRecord() : null;
  if (syncThumb && !latest) {
    setPresetDialogError(ui.presetOverwriteError, "作品库暂无图片，无法同步缩略图");
    return;
  }
  try {
    const body = { settings: presetSnapshot() };
    if (latest) body.source_image_id = latest.id;
    await request(`/api/style-presets/${encodeURIComponent(item.id)}`, {
      method: "PUT",
      body: JSON.stringify(body),
    });
    ui.presetOverwriteDialog.close();
    presetOverwriteTarget = null;
    // 覆盖后强制刷新缩略图缓存版本,避免浏览器复用旧图片。
    presetThumbVersion = Date.now();
    await loadStylePresets();
    toast(`已覆盖预设：【${item.name}】`);
  } catch (error) {
    setPresetDialogError(ui.presetOverwriteError, error.message);
  }
}

// ---------- 更改预设名:PATCH + 前端校验 ----------
let presetRenameTarget = null;
function openPresetRenameDialog(item) {
  presetRenameTarget = item;
  ui.presetRenameName.value = item.name;
  setPresetDialogError(ui.presetRenameError);
  ui.presetRenameDialog.showModal();
  ui.presetRenameName.focus();
  ui.presetRenameName.select();
}
async function submitPresetRename() {
  const item = presetRenameTarget;
  if (!item) return;
  const name = ui.presetRenameName.value.trim();
  if (!name || name.length > 100) {
    setPresetDialogError(ui.presetRenameError, "预设名称需要 1-100 个字符");
    return;
  }
  const duplicated = stylePresets.some(
    (other) => other.id !== item.id && other.name.trim().toLocaleLowerCase() === name.toLocaleLowerCase(),
  );
  if (duplicated) {
    setPresetDialogError(ui.presetRenameError, "已有同名风格预设");
    return;
  }
  if (name === item.name) {
    ui.presetRenameDialog.close();
    presetRenameTarget = null;
    return;
  }
  try {
    await request(`/api/style-presets/${encodeURIComponent(item.id)}`, {
      method: "PATCH",
      body: JSON.stringify({ name }),
    });
    ui.presetRenameDialog.close();
    presetRenameTarget = null;
    await loadStylePresets();
    toast(`已重命名预设：【${name}】`);
  } catch (error) {
    setPresetDialogError(ui.presetRenameError, error.message);
  }
}

// ---------- 预设归类:多选收藏夹弹窗 ----------
function setPresetCollectionsError(message = "") {
  if (!ui.presetCollectionsError) return;
  ui.presetCollectionsError.textContent = message;
  ui.presetCollectionsError.hidden = !message;
}

// ---------- 重构:二级归类列表渲染 ----------
function renderPresetCollectionsChecklist(checkedIds = []) {
  const container = ui.presetCollectionsChecklist;
  if (!container) return;

  const checked = new Set(checkedIds.map(Number));
  const elements = [];

  // 1. 独立顶部项:★ 默认收藏(ID: 1)
  const defaultCol = presetCollections.find((c) => Number(c.id) === DEFAULT_COLLECTION_ID);
  if (defaultCol) {
    const favLabel = document.createElement("label");
    favLabel.className = "favorite-group-check preset-default-fav-row";
    favLabel.innerHTML = `
      <input type="checkbox" value="${DEFAULT_COLLECTION_ID}" ${checked.has(DEFAULT_COLLECTION_ID) ? "checked" : ""}>
      <span style="font-weight: 600; color: var(--favorite);">★ ${escapeHtml(defaultCol.name || "默认收藏")}</span>
      <small style="margin-left: auto; color: var(--text-tertiary); font-size: 10px;">${Number(defaultCol.count || 0)} 项</small>
    `;
    elements.push(favLabel);
  }

  // 2. 提取所有自定义母文件夹(parent_id 为空且排除 ID 1)
  const parents = presetCollections
    .filter((c) => c.parent_id == null && Number(c.id) !== DEFAULT_COLLECTION_ID)
    .sort((a, b) => Number(a.id) - Number(b.id));

  if (!parents.length && !defaultCol) {
    const emptyP = document.createElement("p");
    emptyP.className = "import-hint";
    emptyP.textContent = "暂无可用的预设分类，请先在下方快捷创建。";
    container.replaceChildren(emptyP);
    return;
  }

  // 3. 循环渲染各母文件夹及其名下子文件夹
  for (const parent of parents) {
    const pid = Number(parent.id);
    const card = document.createElement("div");
    card.className = "preset-parent-group-card";

    // 母文件夹头部标头(纯容器,不带复选框)
    const header = document.createElement("div");
    header.className = "preset-parent-group-header";
    header.innerHTML = `
      <span class="preset-parent-group-title">
        <span aria-hidden="true">📁</span> ${escapeHtml(parent.name)}
      </span>
      <span class="preset-parent-group-count">${Number(parent.count || 0)} 项</span>
    `;
    card.append(header);

    // 提取直属于该母分类的所有子文件夹
    const subs = presetCollections
      .filter((c) => Number(c.parent_id) === pid)
      .sort((a, b) => Number(a.id) - Number(b.id));

    const subGrid = document.createElement("div");
    subGrid.className = "preset-sub-checklist-grid";

    if (!subs.length) {
      const note = document.createElement("span");
      note.className = "preset-sub-empty-note";
      note.textContent = "该母类下暂无子分类";
      subGrid.append(note);
    } else {
      for (const sub of subs) {
        const sid = Number(sub.id);
        const itemLabel = document.createElement("label");
        itemLabel.className = "preset-sub-check-item";
        itemLabel.innerHTML = `
          <input type="checkbox" value="${sid}" ${checked.has(sid) ? "checked" : ""}>
          <span class="preset-sub-check-name" title="${escapeHtml(sub.name)}">${escapeHtml(sub.name)}</span>
          <span class="preset-sub-check-badge">${Number(sub.count || 0)}</span>
        `;
        subGrid.append(itemLabel);
      }
    }

    card.append(subGrid);
    elements.push(card);
  }

  container.replaceChildren(...elements);
  syncPresetDialogParentSelect();
}

// 刷新弹窗内部母文件夹下拉选单
function syncPresetDialogParentSelect() {
  const select = ui.presetDialogParentSelect;
  if (!select) return;

  const parents = presetCollections.filter(
    (c) => c.parent_id == null && Number(c.id) !== DEFAULT_COLLECTION_ID
  );

  select.replaceChildren(
    ...parents.map((p) => new Option(p.name, String(p.id)))
  );

  // 默认预选当前主视图正在查看的母分类
  if (currentPresetParentId > 1 && parents.some((p) => Number(p.id) === currentPresetParentId)) {
    select.value = String(currentPresetParentId);
  } else if (parents.length > 0) {
    select.value = String(parents[0].id);
  }
}

// 严格防守:只收集子文件夹 ID 以及默认收藏 ID 1,过滤掉任何可能误入的母文件夹 ID
function checkedPresetCollectionIds() {
  if (!ui.presetCollectionsChecklist) return [];
  const validLeafIds = new Set(
    presetCollections
      .filter((c) => c.parent_id != null || Number(c.id) === DEFAULT_COLLECTION_ID)
      .map((c) => Number(c.id))
  );

  return [...ui.presetCollectionsChecklist.querySelectorAll('input[type="checkbox"]:checked')]
    .map((input) => Number(input.value))
    .filter((id) => Number.isFinite(id) && validLeafIds.has(id));
}

// 弹窗内快捷创建子文件夹:创建成功后立即勾选并保持其余已选项不变
async function createAndCheckPresetSubCollection() {
  const select = ui.presetDialogParentSelect;
  const input = ui.presetDialogSubNameInput;
  const btn = ui.btnPresetDialogCreateAndCheck;

  const parentId = Number(select?.value);
  const name = (input?.value || "").trim();

  if (!parentId) {
    setPresetCollectionsError("请先选择所属的母文件夹");
    select?.focus();
    return;
  }
  if (!name) {
    setPresetCollectionsError("子文件夹名称不能为空");
    input?.focus();
    return;
  }

  if (btn) btn.disabled = true;
  setPresetCollectionsError("");

  try {
    const created = await request("/api/style-presets/collections", {
      method: "POST",
      body: JSON.stringify({ name, parent_id: parentId }),
    });

    // 重新获取全量分类
    await loadPresetCollections();

    // 提取当前弹窗中已经勾选的 ID 集合,并将刚创建的子类 ID 立即打勾
    const currentlyChecked = checkedPresetCollectionIds();
    const newId = Number(created?.id);
    if (newId && !currentlyChecked.includes(newId)) {
      currentlyChecked.push(newId);
    }

    // 重绘弹窗勾选树并保持回显
    renderPresetCollectionsChecklist(currentlyChecked);
    if (input) input.value = "";
    toast(`已成功创建子分类“${name}”并自动勾选`);
  } catch (error) {
    setPresetCollectionsError(error.message || "创建子分类失败");
  } finally {
    if (btn) btn.disabled = false;
  }
}

function openPresetCollectionsDialog(item) {
  // 单预设归类前复位批量上下文,避免弹窗沿用批量标题与提交分支。
  presetBatchCollectionsContext = null;
  presetCollectionsTarget = item;
  setPresetCollectionsError("");

  if (ui.presetCollectionsTitle) ui.presetCollectionsTitle.textContent = "归类风格预设";
  if (ui.presetCollectionsSummary) {
    ui.presetCollectionsSummary.textContent = `选择预设【${item.name}】归属的子文件夹（支持同时归属多个分类）：`;
  }

  // 回显该预设当前的子分类归属
  renderPresetCollectionsChecklist(presetCollectionIds(item));
  ui.presetCollectionsDialog.showModal();
}

async function submitPresetCollections() {
  const item = presetCollectionsTarget;
  if (!item || presetCollectionsSaving) return;
  const collectionIds = checkedPresetCollectionIds();
  presetCollectionsSaving = true;
  const submitButton = ui.presetCollectionsForm?.querySelector('button[type="submit"]');
  if (submitButton) submitButton.disabled = true;
  setPresetCollectionsError("");
  try {
    const result = await request(`/api/style-presets/${encodeURIComponent(item.id)}/collections`, {
      method: "POST",
      body: JSON.stringify({ collection_ids: collectionIds }),
    });
    const updated = Array.isArray(result?.collection_ids)
      ? result.collection_ids.map(Number)
      : collectionIds;
    item.collection_ids = updated;
    item.favorite = updated.includes(DEFAULT_COLLECTION_ID);
    ui.presetCollectionsDialog.close();
    presetCollectionsTarget = null;
    // 归类会改变各分类归属,重新拉取统计以保证徽标与卡片严格同步。
    await loadPresetCollections();
    toast("已更新预设归类");
  } catch (error) {
    setPresetCollectionsError(error.message);
  } finally {
    presetCollectionsSaving = false;
    if (submitButton) submitButton.disabled = false;
  }
}

// ---------- 删除预设:二次确认 + 淡出移除 ----------
let presetDeleteTarget = null;
function openPresetDeleteDialog(item) {
  // 单预设删除前复位批量上下文,避免弹窗沿用批量标题与提交分支。
  presetBatchDeleteContext = null;
  presetDeleteTarget = item;
  const title = ui.presetDeleteDialog?.querySelector(".dialog-heading h2");
  if (title) title.textContent = "删除预设";
  ui.presetDeleteSummary.textContent = `确定删除预设【${item.name}】吗？此操作无法撤销。`;
  setPresetDialogError(ui.presetDeleteError);
  ui.presetDeleteDialog.showModal();
}
async function submitPresetDelete() {
  const item = presetDeleteTarget;
  if (!item) return;
  try {
    await request(`/api/style-presets/${encodeURIComponent(item.id)}`, { method: "DELETE" });
    ui.presetDeleteDialog.close();
    presetDeleteTarget = null;
    stylePresets = stylePresets.filter((preset) => preset.id !== item.id);
    presetAllTotal = stylePresets.length;
    // 删除后同步各分类徽标,避免计数与实际归属脱节。
    renderPresetCollections();
    const card = ui.presetGrid.querySelector(`.preset-card[data-preset-id="${CSS.escape(item.id)}"]`);
    if (card) {
      card.classList.add("is-removing");
      card.addEventListener("animationend", () => renderStylePresets(), { once: true });
      // 兜底:动画事件缺失时仍保证卡片被移除。
      setTimeout(() => renderStylePresets(), 400);
    } else {
      renderStylePresets();
    }
    toast(`已删除预设：【${item.name}】`);
  } catch (error) {
    setPresetDialogError(ui.presetDeleteError, error.message);
  }
}

// ---------- 新建预设:模态框 + 封面选择 ----------
let presetCreateCover = { blob: null, objectUrl: null, sourceId: null };
// 同步读取当前分页内存中的最新记录(仅作降级回退使用)。
function latestHistoryRecord() {
  return Array.isArray(historyItems) && historyItems.length ? historyItems[0] : null;
}
// 异步获取全库(不限收藏夹、不受当前分页影响)最新作品。
// 失败时降级回退到当前分页内存中的首条记录。
async function fetchLatestHistoryRecord() {
  try {
    const data = await request("/api/history?page=1&limit=1&collection_id=0");
    const items = Array.isArray(data?.items) ? data.items : [];
    return items.length ? items[0] : null;
  } catch (error) {
    console.warn("获取全库最新作品失败:", error);
    // 降级回退
    return Array.isArray(historyItems) && historyItems.length ? historyItems[0] : null;
  }
}
// 覆盖更新后手动递增的缓存版本号,用于强制浏览器重新拉取缩略图。
let presetThumbVersion = 0;
// 预设缩略图 URL 追加版本参数,避免覆盖更新后浏览器命中旧图片缓存。
function presetThumbnailUrl(item) {
  const base = item?.thumbnail_url || `/api/style-presets/${encodeURIComponent(item?.id)}/thumbnail`;
  const version = [item?.updated_at || item?.created_at || "", presetThumbVersion]
    .filter(Boolean)
    .join("-");
  if (!version) return base;
  const separator = base.includes("?") ? "&" : "?";
  return `${base}${separator}v=${encodeURIComponent(version)}`;
}
function setPresetDialogError(element, message = "") {
  element.textContent = message;
  element.hidden = !message;
}
async function resetPresetCreateCover() {
  if (presetCreateCover.objectUrl) URL.revokeObjectURL(presetCreateCover.objectUrl);
  presetCreateCover = { blob: null, objectUrl: null, sourceId: null };
  // 默认封面取全库最新作品,不受当前分页与收藏夹筛选影响。
  const latest = await fetchLatestHistoryRecord();
  if (latest) {
    presetCreateCover.sourceId = latest.id;
    ui.presetCreatePreview.src = `/api/images/${latest.id}`;
    ui.presetCreatePreview.hidden = false;
    ui.presetCreatePlaceholder.hidden = true;
    ui.presetCreateCoverHint.textContent = "默认使用作品库最新生成图作为封面。";
  } else {
    ui.presetCreatePreview.hidden = true;
    ui.presetCreatePreview.removeAttribute("src");
    ui.presetCreatePlaceholder.hidden = false;
    ui.presetCreateCoverHint.textContent = "作品库暂无图片，可上传本地图片作为封面。";
  }
}
async function openPresetCreateDialog() {
  ui.presetCreateName.value = "";
  setPresetDialogError(ui.presetCreateError);
  await resetPresetCreateCover();
  ui.presetCreateDialog.showModal();
  ui.presetCreateName.focus();
}
function applyPresetCreateFile(file) {
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    setPresetDialogError(ui.presetCreateError, "请选择图片文件");
    return;
  }
  if (presetCreateCover.objectUrl) URL.revokeObjectURL(presetCreateCover.objectUrl);
  presetCreateCover.blob = file;
  presetCreateCover.sourceId = null;
  presetCreateCover.objectUrl = URL.createObjectURL(file);
  ui.presetCreatePreview.src = presetCreateCover.objectUrl;
  ui.presetCreatePreview.hidden = false;
  ui.presetCreatePlaceholder.hidden = true;
  ui.presetCreateCoverHint.textContent = `已选择本地图片：${file.name}`;
  setPresetDialogError(ui.presetCreateError);
}
// ---------- 从作品库选择封面 ----------
let pickerHistoryPage = 1;
let pickerHistoryPages = 1;
let selectedPickerRecord = null;
let pickerHistoryRequest = 0;
const HISTORY_PICKER_LIMIT = 18;

function renderHistoryPickerItems(items) {
  ui.historyPickerGrid.replaceChildren(
    ...items.map((record) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "history-picker-item";
      button.dataset.recordId = String(record.id);
      button.setAttribute("aria-label", `选择作品 ${record.filename || record.id}`);
      button.innerHTML = `<img loading="lazy" decoding="async" src="/api/images/${record.id}" alt="${escapeHtml(record.filename || "作品缩略图")}">`;
      if (selectedPickerRecord && String(selectedPickerRecord.id) === String(record.id)) {
        button.classList.add("selected");
      }
      button.addEventListener("click", () => selectHistoryPickerRecord(record, button));
      button.addEventListener("dblclick", () => {
        selectHistoryPickerRecord(record, button);
        applyHistoryPickerSelection();
      });
      return button;
    }),
  );
}

function selectHistoryPickerRecord(record, button) {
  selectedPickerRecord = record;
  ui.historyPickerGrid.querySelectorAll(".history-picker-item.selected").forEach((item) => item.classList.remove("selected"));
  button.classList.add("selected");
  ui.confirmHistoryPicker.disabled = false;
}

function updateHistoryPickerPager() {
  ui.historyPickerPageLabel.textContent = `${pickerHistoryPage} / ${pickerHistoryPages}`;
  ui.historyPickerPrev.disabled = pickerHistoryPage <= 1;
  ui.historyPickerNext.disabled = pickerHistoryPage >= pickerHistoryPages;
}

async function loadHistoryPicker(page = 1) {
  const requestId = ++pickerHistoryRequest;
  try {
    const data = await request(`/api/history?page=${page}&limit=${HISTORY_PICKER_LIMIT}`);
    if (requestId !== pickerHistoryRequest) return;
    pickerHistoryPage = Number(data.page) || 1;
    pickerHistoryPages = Number(data.pages) || 1;
    const items = Array.isArray(data.items) ? data.items : [];
    renderHistoryPickerItems(items);
    ui.historyPickerEmpty.hidden = items.length > 0;
    updateHistoryPickerPager();
  } catch (error) {
    if (requestId !== pickerHistoryRequest) return;
    toast(error.message);
  }
}

function openHistoryPicker() {
  selectedPickerRecord = null;
  ui.confirmHistoryPicker.disabled = true;
  ui.historyPickerDialog.showModal();
  loadHistoryPicker(1);
}

function applyHistoryPickerSelection() {
  if (!selectedPickerRecord) return;
  if (presetCreateCover.objectUrl) URL.revokeObjectURL(presetCreateCover.objectUrl);
  presetCreateCover.blob = null;
  presetCreateCover.objectUrl = null;
  presetCreateCover.sourceId = selectedPickerRecord.id;
  ui.presetCreatePreview.src = `/api/images/${selectedPickerRecord.id}`;
  ui.presetCreatePreview.hidden = false;
  ui.presetCreatePlaceholder.hidden = true;
  ui.presetCreateCoverHint.textContent = `已选择作品库图片：#${selectedPickerRecord.sequence || ""} (${selectedPickerRecord.filename || ""})`;
  ui.historyPickerDialog.close();
}

async function submitPresetCreate() {
  const name = ui.presetCreateName.value.trim();
  if (!name || name.length > 100) {
    setPresetDialogError(ui.presetCreateError, "预设名称需要 1-100 个字符");
    return;
  }
  if (stylePresets.some((item) => item.name.trim().toLocaleLowerCase() === name.toLocaleLowerCase())) {
    setPresetDialogError(ui.presetCreateError, "已有同名预设，请改名或使用覆盖按钮");
    return;
  }
  const submitButton = ui.presetCreateForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  try {
    let created;
    if (presetCreateCover.blob) {
      const form = new FormData();
      form.append("name", name);
      form.append("favorite", "false");
      form.append("settings", JSON.stringify(presetSnapshot()));
      form.append("thumbnail", presetCreateCover.blob, presetCreateCover.blob.name || "cover.png");
      created = await request("/api/style-presets", { method: "POST", body: form });
    } else {
      const body = { name, favorite: false, settings: presetSnapshot() };
      if (presetCreateCover.sourceId != null) body.source_image_id = presetCreateCover.sourceId;
      created = await request("/api/style-presets", { method: "POST", body: JSON.stringify(body) });
    }
    // ===== 新增体验优化:若当前正在具体子分类下,自动为新预设绑定该子分类 =====
    if (currentPresetSubId > 0) {
      try {
        const updateRes = await request(
          `/api/style-presets/${encodeURIComponent(created.id)}/collections`,
          {
            method: "POST",
            body: JSON.stringify({ collection_ids: [currentPresetSubId] }),
          },
        );
        created.collection_ids = Array.isArray(updateRes?.collection_ids)
          ? updateRes.collection_ids.map(Number)
          : [currentPresetSubId];
      } catch (e) {
        console.warn("自动绑定当前子分类失败:", e);
      }
    }

    ui.presetCreateDialog.close();
    resetPresetCreateCover();
    // 新预设始终按时间顺序追加到数组首位,不再寻找非收藏项插入。
    stylePresets.unshift(created);
    presetAllTotal = stylePresets.length;
    // 停留在当前视图:若在具体子分类下新建,新预设可直接出现在当前列表中。
    presetPage = 1;
    // 归类会改变各分类归属,重新拉取统计以保证徽标与卡片严格同步。
    await loadPresetCollections();
    renderPresetCollections();
    renderPresetSubCollections();
    renderStylePresets();
    toast(`已新建预设：【${created.name}】`);
  } catch (error) {
    setPresetDialogError(ui.presetCreateError, error.message);
  } finally {
    submitButton.disabled = false;
  }
}
function switchMainTab(tab) {
  const showPresets = tab === "presets";
  // Tab 互斥:切换视图时退出两种批量模式,防止悬浮条与选择集合串味。
  if (showPresets) {
    if (isBatchMode) setBatchMode(false);
  } else if (isPresetBatchMode) {
    setPresetBatchMode(false);
  }
  ui.tabBtnGallery.classList.toggle("active", !showPresets);
  ui.tabBtnPresets.classList.toggle("active", showPresets);
  ui.tabBtnGallery.setAttribute("aria-selected", String(!showPresets));
  ui.tabBtnPresets.setAttribute("aria-selected", String(showPresets));
  ui.galleryViewContainer.hidden = showPresets;
  ui.presetsViewContainer.hidden = !showPresets;
}
async function updateStylePreset(item, changes) {
  try {
    await request(`/api/style-presets/${encodeURIComponent(item.id)}`, {
      method: "PUT",
      body: JSON.stringify(changes),
    });
    await loadStylePresets();
  } catch (error) {
    toast(error.message);
  }
}
function setPromptRuleError(message = "") {
  ui.promptRuleError.textContent = message;
  ui.promptRuleError.hidden = !message;
}
function clearPromptRuleEditor() {
  editingPromptRule = null;
  ui.promptRuleId.value = "";
  ui.promptRuleFrom.value = "";
  ui.promptRuleTo.value = "";
  ui.promptRulePositive.checked = true;
  ui.promptRuleNegative.checked = true;
  ui.promptRuleLora.checked = false;
  ui.deletePromptRule.hidden = true;
  setPromptRuleError();
}
function editPromptRule(item) {
  if (item.kind !== "custom") return;
  editingPromptRule = item;
  ui.promptRuleId.value = item.id;
  ui.promptRuleFrom.value = item.from || "";
  ui.promptRuleTo.value = item.to || "";
  ui.promptRulePositive.checked = item.scopes?.includes("positive");
  ui.promptRuleNegative.checked = item.scopes?.includes("negative");
  ui.promptRuleLora.checked = item.scopes?.includes("lora");
  ui.deletePromptRule.hidden = false;
  setPromptRuleError();
  ui.promptRuleFrom.focus();
}
function renderPromptRules() {
  ui.promptRuleList.replaceChildren(
    ...promptRules.map((item) => {
      const row = document.createElement("div");
      row.className = `prompt-rule-row${item.enabled ? "" : " disabled"}`;
      const description =
        item.kind === "builtin"
          ? item.description
          : `${item.from} → ${item.to} · ${(item.scopes || []).join(" / ")}`;
      const ruleName = item.kind === "builtin" ? item.name : item.from;
      row.innerHTML = `<div class="prompt-rule-copy"><strong>${escapeHtml(ruleName)}</strong><small title="${escapeHtml(description)}">${escapeHtml(description)}</small></div><div class="prompt-rule-actions"><label class="compact-check"><input type="checkbox" ${item.enabled ? "checked" : ""} aria-label="${escapeHtml(ruleName)}：${item.enabled ? "停用" : "启用"}规则"><span>${item.enabled ? "启用" : "停用"}</span></label>${item.kind === "custom" ? '<button class="button ghost compact" type="button">编辑</button>' : ""}</div>`;
      row.querySelector('input[type="checkbox"]').addEventListener("change", async (event) => {
        try {
          await request(`/api/prompt-rules/${encodeURIComponent(item.id)}`, {
            method: "PUT",
            body: JSON.stringify({ enabled: event.target.checked }),
          });
          await loadPromptRules();
        } catch (error) {
          toast(error.message);
          await loadPromptRules();
        }
      });
      row.querySelector("button")?.addEventListener("click", () => editPromptRule(item));
      return row;
    }),
  );
}
async function loadPromptRules() {
  const data = await request("/api/prompt-rules");
  promptRules = data.items || [];
  renderPromptRules();
}
async function openPromptRuleDialog() {
  clearPromptRuleEditor();
  ui.promptRuleDialog.showModal();
  try {
    await loadPromptRules();
  } catch (error) {
    setPromptRuleError(error.message);
  }
}
function promptRuleScopes() {
  return [
    ui.promptRulePositive.checked ? "positive" : "",
    ui.promptRuleNegative.checked ? "negative" : "",
    ui.promptRuleLora.checked ? "lora" : "",
  ].filter(Boolean);
}
async function savePromptRule(event) {
  event.preventDefault();
  const scopes = promptRuleScopes();
  if (!scopes.length) {
    setPromptRuleError("至少选择一个应用范围");
    return;
  }
  const payload = {
    from: ui.promptRuleFrom.value,
    to: ui.promptRuleTo.value,
    scopes,
    enabled: true,
  };
  try {
    const path = editingPromptRule
      ? `/api/prompt-rules/${encodeURIComponent(editingPromptRule.id)}`
      : "/api/prompt-rules";
    await request(path, {
      method: editingPromptRule ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    clearPromptRuleEditor();
    await loadPromptRules();
    toast("提示词替换规则已保存");
  } catch (error) {
    setPromptRuleError(error.message);
  }
}
async function deletePromptRule() {
  if (!editingPromptRule) return;
  try {
    await request(`/api/prompt-rules/${encodeURIComponent(editingPromptRule.id)}`, {
      method: "DELETE",
    });
    clearPromptRuleEditor();
    await loadPromptRules();
    toast("提示词替换规则已删除");
  } catch (error) {
    setPromptRuleError(error.message);
  }
}

function artistName(value) {
  let name = String(value || "").trim();
  if (name.startsWith("@")) name = name.slice(1).trim();
  else if (name.toLowerCase().startsWith("by ")) name = name.slice(3).trim();
  return name;
}
function artistTokensFrom(value) {
  const values = String(value || "")
    .replaceAll("\r", ",")
    .replaceAll("\n", ",")
    .split(/,|(?=@)/)
    .map(artistName)
    .filter(Boolean);
  const seen = new Set();
  return values.filter((name) => {
    const key = name.toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
function canonicalArtists(value) {
  return artistTokensFrom(value)
    .map((name) => `@${name}`)
    .join(", ");
}
function artistTokens() {
  return artistTokensFrom(ui.manual_artist.value);
}
function appendArtist(name) {
  const values = artistTokens();
  const keys = new Set(values.map((value) => value.toLowerCase()));
  const clean = artistName(name);
  if (clean && !keys.has(clean.toLowerCase())) values.push(clean);
  ui.manual_artist.value = values.map((value) => `@${value}`).join(", ");
  schedulePersist();
}
function artistEditingValue(value) {
  return String(value || "")
    .replaceAll("\r", ",")
    .replaceAll("\n", ",")
    .split(",")
    .map((part) => {
      const leading = part.match(/^\s*/)?.[0] || "";
      let name = part.slice(leading.length);
      if (/^by\s+/i.test(name)) name = name.replace(/^by\s+/i, "@");
      else if (name && !name.startsWith("@")) name = `@${name}`;
      return name;
    })
    .join(", ");
}
function normalizeArtistField(finalize = false) {
  const input = ui.manual_artist;
  const raw = input.value;
  const caret = input.selectionStart ?? raw.length;
  const transform = finalize ? canonicalArtists : artistEditingValue;
  const next = transform(raw);
  if (next === raw) return;
  const nextCaret = transform(raw.slice(0, caret)).length;
  input.value = next;
  if (document.activeElement === input) input.setSelectionRange(nextCaret, nextCaret);
}
async function loadArtistFavorites() {
  try {
    artistFavoritesData = await request("/api/favorites/artist");
  } catch {
    artistFavoritesData = { groups: [], items: [] };
  }
  renderArtistFavorites();
}
let artistSearchQuery = "";

function renderArtistFavorites() {
  const allItems = (artistFavoritesData.items || []).filter((item) => item.groupIds?.length);
  ui.artistFavoriteCount.textContent = `${allItems.length} 位`;

  // 1. 渲染主面板折叠菜单中的胶囊快捷入口 (仅展示前 12 个)
  ui.artistFavorites.replaceChildren(
    ...allItems.slice(0, 12).map((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "artist-chip";
      button.title = item.nickname ? `追加 @${item.name} · ${item.nickname}` : `追加 @${item.name}`;
      button.innerHTML = `<strong>@${escapeHtml(item.name)}</strong>${item.nickname ? `<small>${escapeHtml(item.nickname)}</small>` : ""}`;
      button.addEventListener("click", () => appendArtist(item.name));
      return button;
    }),
  );

  // 2. 根据搜索词过滤弹窗内的画师列表
  const query = (artistSearchQuery || "").trim().toLowerCase();
  const filteredItems = query
    ? allItems.filter(
        (item) =>
          item.name.toLowerCase().includes(query) ||
          (item.nickname && item.nickname.toLowerCase().includes(query)),
      )
    : allItems;

  // 3. 渲染弹窗内画师列表
  if (!filteredItems.length) {
    ui.artistFavoriteList.replaceChildren(
      Object.assign(document.createElement("div"), {
        className: "artist-favorite-empty",
        textContent: query ? "没有找到匹配的画师" : "还没有收藏画师，可在上方直接添加",
      }),
    );
    return;
  }

  ui.artistFavoriteList.replaceChildren(
    ...filteredItems.map((item) => {
      const row = document.createElement("div");
      row.className = "artist-favorite-row";
      row.innerHTML = `
        <button class="artist-favorite-name" type="button" title="点击追加到固定画师">
          <strong>@${escapeHtml(item.name)}</strong>
          ${item.nickname ? `<small>${escapeHtml(item.nickname)}</small>` : ""}
        </button>
        <button class="button ghost compact btn-append-artist" type="button">追加</button>
        <button class="icon-button dark btn-remove-artist" type="button" title="取消收藏" aria-label="取消收藏">×</button>
      `;
      row.querySelector(".artist-favorite-name").addEventListener("click", () => appendArtist(item.name));
      row.querySelector(".btn-append-artist").addEventListener("click", () => appendArtist(item.name));
      row.querySelector(".btn-remove-artist").addEventListener("click", () => removeArtistFavorite(item.name));
      return row;
    }),
  );
}
async function openArtistDialog() {
  // 重置输入状态
  artistSearchQuery = "";
  if (ui.artistSearchInput) ui.artistSearchInput.value = "";
  if (ui.newArtistInput) ui.newArtistInput.value = "";
  if (ui.newArtistNickname) ui.newArtistNickname.value = "";

  await loadArtistFavorites();
  ui.artistDialog.showModal();
  ui.newArtistInput?.focus();
}
async function saveCurrentArtistFavorites() {
  const values = artistTokens();
  if (!values.length) {
    toast("请先输入画师名称");
    return;
  }
  try {
    for (const name of values)
      artistFavoritesData = await request("/api/favorites/artist/item", {
        method: "PUT",
        body: JSON.stringify({ name, favorite: true }),
      });
    renderArtistFavorites();
    toast(`已收藏 ${values.length} 位画师`);
  } catch (error) {
    toast(error.message);
  }
}
async function addSingleArtistFavorite() {
  const nameInput = ui.newArtistInput;
  const nickInput = ui.newArtistNickname;
  if (!nameInput) return;

  const rawName = nameInput.value.trim();
  const cleanName = artistName(rawName); // 自动清洗，去除用户误输入的 @ 或 by 前缀
  const nickname = nickInput ? nickInput.value.trim() : "";

  if (!cleanName) {
    toast("请输入有效的画师名");
    nameInput.focus();
    return;
  }

  // 检查是否已在收藏列表中
  const existing = (artistFavoritesData.items || []).find(
    (item) => item.name.toLowerCase() === cleanName.toLowerCase() && item.groupIds?.length,
  );
  if (existing) {
    toast(`画师 @${cleanName} 已在收藏列表中`);
    nameInput.focus();
    return;
  }

  try {
    const payload = {
      name: cleanName,
      favorite: true,
    };
    if (nickname) payload.nickname = nickname;

    artistFavoritesData = await request("/api/favorites/artist/item", {
      method: "PUT",
      body: JSON.stringify(payload),
    });

    // 成功后清空输入框并聚焦
    nameInput.value = "";
    if (nickInput) nickInput.value = "";
    nameInput.focus();

    renderArtistFavorites();
    toast(`已收藏画师：@${cleanName}`);
  } catch (error) {
    toast(`添加失败: ${error.message}`);
  }
}
async function removeArtistFavorite(name) {
  try {
    artistFavoritesData = await request("/api/favorites/artist/item", {
      method: "PUT",
      body: JSON.stringify({ name, favorite: false }),
    });
    renderArtistFavorites();
    toast("已取消收藏画师");
  } catch (error) {
    toast(error.message);
  }
}

async function submitBatch(settings, seeds = null) {
  // 统一的批次提交入口:主表单、复现、变体共用;in-flight 守卫防双击重复入队。
  if (submitInFlight) return false;
  submitInFlight = true;
  ui.startButton.disabled = true;
  try {
    settings = await normalizeSettingsPayload(settings);
    const body = seeds ? { ...settings, seeds } : settings;
    const state = await request("/api/batches", { method: "POST", body: JSON.stringify(body) });
    if (state.status === "queued") toast(`已加入队列,第 ${state.position} 位`);
    else toast("批次已开始");
    return true;
  } catch (error) {
    toast(error.message);
    await refreshConnection();
    return false;
  } finally {
    submitInFlight = false;
    try {
      renderBatchPayload(await request("/api/batches/current"));
    } catch {
      ui.startButton.disabled = !ui.connection.classList.contains("online");
    }
  }
}
ui.settingsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await normalizePromptFields(currentPromptFields());
    persistNow();
    await submitBatch(readSettings());
  } catch (error) {
    toast(error.message);
  }
});
ui.settingsForm.addEventListener("input", (event) => {
  if (event.target.matches("input, textarea, select")) schedulePersist();
});
ui.settingsForm.addEventListener("change", schedulePersist);
ui.stopButton.addEventListener("click", async () => {
  if (!currentBatch) return;
  try {
    // 停止 = 中断当前批次并清空队列(队列条目可单独用 × 移除)
    renderBatchPayload(await request(`/api/batches/${currentBatch.id}/stop`, { method: "POST" }));
  } catch (error) {
    toast(error.message);
  }
});
// Animated collapse for <details> sections: intercept the toggle, play the
// reverse of the `disclose` entry animation, then flip `open` off.
for (const details of document.querySelectorAll("details.advanced-section, details.artist-favorites-section")) {
  const summary = details.querySelector("summary");
  const content = details.querySelector(".details-content, .artist-favorites-content, summary + *");
  if (!summary || !content) continue;
  summary.addEventListener("click", (event) => {
    if (!details.open || details.dataset.collapsing) return;
    event.preventDefault();
    details.dataset.collapsing = "1";
    const animation = content.animate(
      [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(-6px)" }],
      { duration: imagePreviewReducedMotion() ? 60 : 180, easing: "cubic-bezier(.4,0,1,1)", fill: "both" },
    );
    animation.finished.then(() => {
      details.open = false;
      delete details.dataset.collapsing;
      animation.cancel(); // release the fill so CSS takes over cleanly
    }).catch(() => {
      details.open = false;
      delete details.dataset.collapsing;
    });
  });
}

ui.queueBadge?.addEventListener("click", () => {
  const open = !ui.queuePanel.classList.contains("open") && currentQueue.length > 0;
  setQueuePanelOpen(open);
  ui.queueBadge.setAttribute("aria-expanded", String(open));
});
ui.reproduceImage?.addEventListener("click", () => openRegenerationDrawer("replay", ui.reproduceImage));
ui.variantButton?.addEventListener("click", () => openRegenerationDrawer("variant", ui.variantButton));
ui.closeReplayDrawer.addEventListener("click", () => closeRegenerationDrawers());
ui.closeVariantDrawer.addEventListener("click", () => closeRegenerationDrawers());
ui.confirmReplay.addEventListener("click", () => submitRegeneration("replay"));
ui.confirmVariant.addEventListener("click", () => {
  const mode = selectedRegenerationMode();
  const count = Math.max(1, Math.min(100, Number(ui.variantDrawerCount.value) || 4));
  submitRegeneration(mode, count, selectedRedrawSections());
});
ui.variantModes.addEventListener("change", updateVariantDrawer);
ui.redrawSections.addEventListener("change", updateVariantDrawer);
for (const input of [ui.variantCount, ui.variantDrawerCount])
  input.addEventListener("input", (event) => {
    const count = Math.max(1, Math.min(100, Number(event.target.value) || 4));
    ui.variantCount.value = count;
    ui.variantDrawerCount.value = count;
  });
ui.prevPage.addEventListener("click", () => loadHistory(historyPage - 1));
ui.nextPage.addEventListener("click", () => loadHistory(historyPage + 1));
// ---------- 批量管理事件绑定 ----------
// 底部操作条为作品库与预设库共用:按当前活动 Tab 分发到各自的状态机。
function isPresetsTabActive() {
  return Boolean(ui.presetsViewContainer && !ui.presetsViewContainer.hidden);
}
ui.btnToggleBatchMode?.addEventListener("click", () => setBatchMode(!isBatchMode));
ui.btnTogglePresetBatchMode?.addEventListener("click", () =>
  setPresetBatchMode(!isPresetBatchMode),
);
ui.batchSelectAll?.addEventListener("click", () => {
  if (isPresetsTabActive()) selectAllPresetBatchPage();
  else selectAllBatchPage();
});
ui.batchClearSelection?.addEventListener("click", () => {
  if (isPresetsTabActive()) clearPresetBatchSelection();
  else clearBatchSelection();
});
ui.batchExport?.addEventListener("click", () => {
  // 预设库无导出能力,按钮在批量模式下已隐藏,此处仅作防御。
  if (isPresetsTabActive()) return;
  batchExportSelected();
});
ui.batchFavorite?.addEventListener("click", () => {
  if (isPresetsTabActive()) openPresetBatchCollectionsDialog();
  else openBatchFavoriteDialog();
});
ui.batchDelete?.addEventListener("click", () => {
  if (isPresetsTabActive()) openPresetBatchDeleteDialog();
  else openBatchDeleteDialog();
});
ui.batchExit?.addEventListener("click", () => {
  if (isPresetsTabActive()) setPresetBatchMode(false);
  else setBatchMode(false);
});
// 批量模式下按 Esc 退出(详情弹窗/预览打开时由各自模块优先处理)。
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (!isBatchMode && !isPresetBatchMode) return;
  if (ui.detailDialog?.open || ui.imagePreviewDialog?.open) return;
  if (document.querySelector("dialog[open]")) return;
  if (isPresetBatchMode) setPresetBatchMode(false);
  else setBatchMode(false);
});
// 切换主视图 Tab 时自动退出两种批量模式,避免悬浮条与状态串味。
ui.tabBtnPresets?.addEventListener("click", () => {
  if (isBatchMode) setBatchMode(false);
});
ui.tabBtnGallery?.addEventListener("click", () => {
  if (isPresetBatchMode) setPresetBatchMode(false);
});
ui.copyPositivePrompt?.addEventListener("click", () => {
  copyPromptToClipboard(ui.detailPositive.value, ui.copyPositivePrompt, "完整提示词已复制到剪贴板");
});
ui.copyNegativePrompt?.addEventListener("click", () => {
  copyPromptToClipboard(ui.detailNegative.value, ui.copyNegativePrompt, "负面提示词已复制到剪贴板");
});
ui.detailImage.addEventListener("click", openImagePreview);
ui.detailImage.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  event.preventDefault();
  openImagePreview();
});
ui.detailPrevious?.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation(); // 阻止冒泡，避免触发图片的打开全屏预览
  navigateDetail(-1); // 切到画廊前面一张
});
ui.detailNext?.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation(); // 阻止冒泡
  navigateDetail(1); // 切到画廊后面一张
});
ui.detailDialog.addEventListener("keydown", (event) => {
  // 1. 若全屏大图预览打开中，跳过（方向键由全屏模块接管）
  if (imagePreview.phase !== "closed") return;

  // 2. 防误触：若用户光标处于输入框、文本域内，不触发切图
  const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
  const isInputActive = ["input", "textarea", "select"].includes(activeTag) || event.target.matches("input, textarea, select");
  if (isInputActive) return;

  if (event.key === "ArrowLeft") {
    event.preventDefault();
    navigateDetail(-1);
  } else if (event.key === "ArrowRight") {
    event.preventDefault();
    navigateDetail(1);
  } else if (event.key === "c" || event.key === "C") {
    // 键盘挑图流：C 键直接快捷复制当前图片
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    event.preventDefault();
    executeQuickExport();
  }
});
ui.closeImagePreview.addEventListener("click", () => closeImagePreview());
ui.imagePreviewPrevious.addEventListener("click", (event) => navigatePreview(-1, event.currentTarget));
ui.imagePreviewNext.addEventListener("click", (event) => navigatePreview(1, event.currentTarget));
ui.imagePreviewImage.addEventListener("pointerdown", imagePreviewPointerDown);
ui.imagePreviewImage.addEventListener("pointermove", imagePreviewPointerMove);
ui.imagePreviewImage.addEventListener("pointerup", imagePreviewPointerUp);
ui.imagePreviewImage.addEventListener("pointercancel", imagePreviewPointerUp);
ui.imagePreviewImage.addEventListener("lostpointercapture", imagePreviewPointerUp);
ui.imagePreviewDialog.addEventListener("wheel", imagePreviewWheel, { passive: false });
ui.imagePreviewImage.addEventListener("dblclick", (event) => {
  event.preventDefault();
  setImagePreviewZoom(imagePreview.zoom < 1.01 ? 2 : 1, event, true);
});
ui.imagePreviewVeil.addEventListener("pointerdown", (event) => {
  if (event.button === 0) imagePreview.backdropPointer = { id: event.pointerId, x: event.clientX, y: event.clientY };
});
ui.imagePreviewVeil.addEventListener("pointerup", (event) => {
  const start = imagePreview.backdropPointer;
  imagePreview.backdropPointer = null;
  if (start?.id === event.pointerId && Math.hypot(event.clientX - start.x, event.clientY - start.y) < 6) closeImagePreview();
});
ui.imagePreviewDialog.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    event.stopPropagation();
    closeImagePreview();
    return;
  }
  if (event.key === "+" || event.key === "=") {
    event.preventDefault();
    setImagePreviewZoom(imagePreview.zoom + .25, null, true);
  } else if (event.key === "-") {
    event.preventDefault();
    setImagePreviewZoom(imagePreview.zoom - .25, null, true);
  } else if (event.key === "0") {
    event.preventDefault();
    resetImagePreviewTransform();
  } else if (event.key === "ArrowLeft" || event.key === "ArrowRight" || event.key === "ArrowUp" || event.key === "ArrowDown") {
    event.preventDefault();
    if (imagePreview.zoom <= 1.01 && (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
      const navigationButton = event.target instanceof Element ? event.target.closest(".image-preview-nav") : null;
      navigatePreview(event.key === "ArrowLeft" ? -1 : 1, navigationButton);
      return;
    }
    cancelImagePreviewAnimation();
    const amount = event.shiftKey ? 80 : 24;
    imagePreview.x += event.key === "ArrowLeft" ? amount * -1 : event.key === "ArrowRight" ? amount : 0;
    imagePreview.y += event.key === "ArrowUp" ? amount * -1 : event.key === "ArrowDown" ? amount : 0;
    applyImagePreviewTransform();
  }
});
ui.imagePreviewDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeImagePreview();
});
ui.imagePreviewDialog.addEventListener("close", () => {
  if (ui.imagePreviewDialog.open || imagePreview.phase === "closed") return;
  // External close (e.g. detail dialog closing) while opening/open: reset now
  // rather than letting a half-finished entry animation keep the veil alive.
  finishImagePreviewClose(false);
});
ui.detailDialog.addEventListener("close", () => closeImagePreview({ immediate: true, restoreFocus: false }));
new ResizeObserver(() => {
  if (imagePreview.phase === "open") {
    cancelImagePreviewAnimation();
    imagePreview.pointers.clear();
    imagePreview.gesture = imagePreview.tap = null;
    ui.imagePreviewImage.classList.remove("is-interacting");
    layoutImagePreview();
  } else if (imagePreview.phase === "closing") finishImagePreviewClose();
}).observe(ui.imagePreviewStage);
ui.closeDialog.addEventListener("click", () => {
  closeImagePreview({ immediate: true, restoreFocus: false });
  closeRegenerationDrawers(false);
  ui.detailDialog.close();
});
ui.detailDialog.addEventListener("click", (event) => {
  if (event.target === ui.detailDialog) {
    closeImagePreview({ immediate: true, restoreFocus: false });
    closeRegenerationDrawers(false);
    ui.detailDialog.close();
    return;
  }
  if (
    (!ui.replayDrawer.hidden || !ui.variantDrawer.hidden) &&
    !event.target.closest(".regeneration-drawer, .reproduce-actions")
  )
    closeRegenerationDrawers();
});
ui.detailDialog.addEventListener("cancel", (event) => {
  if (!ui.replayDrawer.hidden || !ui.variantDrawer.hidden) {
    event.preventDefault();
    closeRegenerationDrawers();
  }
});
ui.restoreSettings.addEventListener("click", () => {
  if (!selectedRecord) return;
  closeImagePreview({ immediate: true, restoreFocus: false });
  // 使用双轨提取载入:随机池抽卡图片固化实际抽中词条,纯固定词图片保留原词,
  // 避免仅凭 resolved_selection 为空就误判为“未使用”而关闭卡池。
  applyRecordSettings(selectedRecord);
  ui.detailDialog.close();
  schedulePersist();
  toast("已载入历史设置");
});
ui.openFolder.addEventListener("click", async () => {
  if (!selectedRecord || ui.openFolder.disabled) return;
  ui.openFolder.disabled = true;
  try {
    await request(`/api/history/${selectedRecord.id}/open-folder`, { method: "POST" });
    toast("已在文件资源管理器中定位该图片");
  } catch (error) {
    toast(error.message);
  } finally {
    ui.openFolder.disabled = false;
  }
});
// ---------- 导出目录胶囊与快捷复制 ----------
ui.btnSetExportFolder?.addEventListener("click", triggerPickExportFolder);
ui.btnOpenExportFolder?.addEventListener("click", async () => {
  try {
    await request("/api/settings/open-export-folder", { method: "POST" });
  } catch (error) {
    toast(error.message);
  }
});
ui.quickExportImage?.addEventListener("click", executeQuickExport);
// ---------- 删除作品:拟态确认弹窗 + 物理文件同步删除 ----------
function openRecordDeleteDialog() {
  if (!selectedRecord) return;
  // 复用同一弹窗:进入前先复位批量上下文,避免残留批量删除状态。
  batchDeleteContext = null;
  const sequence = selectedRecord.sequence ?? "";
  const filename = selectedRecord.filename || "";
  ui.recordDeleteSummary.textContent = `作品 #${sequence} · ${filename}`;
  const warning = ui.recordDeleteDialog?.querySelector(".record-delete-warning");
  if (warning) {
    warning.textContent = "⚠️ 确定要删除该作品吗？此操作将同步永久删除本地物理图片文件，不可撤销。";
  }
  const title = ui.recordDeleteDialog?.querySelector(".dialog-heading h2");
  if (title) title.textContent = "删除作品";
  setRecordDeleteError("");
  ui.confirmRecordDelete.disabled = false;
  ui.confirmRecordDelete.textContent = "确认删除";
  ui.recordDeleteDialog.showModal();
}

async function submitRecordDelete() {
  const record = selectedRecord;
  if (!record || ui.confirmRecordDelete.disabled) return;
  ui.confirmRecordDelete.disabled = true;
  ui.confirmRecordDelete.textContent = "正在删除...";
  ui.recordDeleteError.textContent = "";
  ui.recordDeleteError.hidden = true;
  try {
    await request(`/api/history/${record.id}`, { method: "DELETE" });
    ui.recordDeleteDialog.close();
    closeImagePreview({ immediate: true, restoreFocus: false });
    ui.detailDialog.close();
    selectedRecord = null;
    updateDetailNavigation();
    await loadHistory(historyPage);
    // 删除后同步刷新胶囊栏计数,避免“全部”与各收藏夹徽标滞后。
    await loadGalleryCollections();
    toast("作品及本地物理文件已删除");
  } catch (error) {
    ui.recordDeleteError.textContent = error.message;
    ui.recordDeleteError.hidden = false;
  } finally {
    ui.confirmRecordDelete.disabled = false;
    ui.confirmRecordDelete.textContent = "确认删除";
  }
}

ui.deleteRecord.addEventListener("click", openRecordDeleteDialog);
// 关闭/取消时按当前上下文复位:批量模式需还原弹窗文案与上下文。
ui.closeRecordDelete.addEventListener("click", () => {
  if (batchDeleteContext) closeBatchDeleteDialog();
  else ui.recordDeleteDialog.close();
});
ui.cancelRecordDelete.addEventListener("click", () => {
  if (batchDeleteContext) closeBatchDeleteDialog();
  else ui.recordDeleteDialog.close();
});
ui.recordDeleteForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (batchDeleteContext) submitBatchDelete();
  else submitRecordDelete();
});
// ---------- 作品库清理:保留最新 N 百张 + 收藏保护 ----------
let cleanupPreviewTimer = null;
let cleanupPreviewToken = 0;
let cleanupPreviewData = null;

function formatCleanupSize(bytes) {
  const value = Number(bytes) || 0;
  if (value <= 0) return "0 MB";
  const mb = value / (1024 * 1024);
  if (mb >= 1024) return `${(mb / 1024).toFixed(2)} GB`;
  return `${mb.toFixed(1)} MB`;
}

function setCleanupError(message) {
  if (!ui.cleanupError) return;
  ui.cleanupError.textContent = message || "";
  ui.cleanupError.hidden = !message;
}

function resetCleanupStats() {
  for (const key of [
    "cleanupStatTotal",
    "cleanupStatKeep",
    "cleanupStatProtected",
    "cleanupStatDelete",
    "cleanupStatSize",
  ]) {
    if (ui[key]) ui[key].textContent = "-";
  }
}

function cleanupKeepHundreds() {
  const value = Number(ui.cleanupKeepHundreds?.value);
  return Number.isFinite(value) && value > 0 ? Math.trunc(value) : 5;
}

async function fetchCleanupPreview() {
  if (!ui.archiveCleanupDialog) return;
  const token = ++cleanupPreviewToken;
  cleanupPreviewData = null;
  setCleanupError("");
  resetCleanupStats();
  if (ui.confirmArchiveCleanup) {
    ui.confirmArchiveCleanup.disabled = true;
    ui.confirmArchiveCleanup.textContent = "计算中...";
  }
  try {
    const data = await request("/api/history/cleanup-preview", {
      method: "POST",
      body: JSON.stringify({ keep_hundreds: cleanupKeepHundreds() }),
    });
    // 竞态守卫:下拉快速切换时丢弃过期响应。
    if (token !== cleanupPreviewToken) return;
    cleanupPreviewData = data;
    if (ui.cleanupStatTotal) ui.cleanupStatTotal.textContent = `${data.total} 张`;
    if (ui.cleanupStatKeep) ui.cleanupStatKeep.textContent = `${data.keep_latest} 张`;
    if (ui.cleanupStatProtected) {
      ui.cleanupStatProtected.textContent = `${data.protected_favorites} 张`;
    }
    if (ui.cleanupStatDelete) ui.cleanupStatDelete.textContent = `${data.to_delete} 张`;
    if (ui.cleanupStatSize) {
      ui.cleanupStatSize.textContent = formatCleanupSize(data.estimated_bytes);
    }
    if (!ui.confirmArchiveCleanup) return;
    if (data.to_delete === 0) {
      ui.confirmArchiveCleanup.disabled = true;
      ui.confirmArchiveCleanup.textContent = "当前无需清理";
    } else {
      ui.confirmArchiveCleanup.disabled = false;
      ui.confirmArchiveCleanup.textContent = "确认永久删除";
    }
  } catch (error) {
    if (token !== cleanupPreviewToken) return;
    setCleanupError(error.message);
    if (ui.confirmArchiveCleanup) {
      ui.confirmArchiveCleanup.disabled = true;
      ui.confirmArchiveCleanup.textContent = "确认清理";
    }
  }
}

function scheduleCleanupPreview() {
  clearTimeout(cleanupPreviewTimer);
  cleanupPreviewTimer = setTimeout(fetchCleanupPreview, 220);
}

function openArchiveCleanupDialog() {
  if (!ui.archiveCleanupDialog) return;
  setCleanupError("");
  resetCleanupStats();
  if (ui.confirmArchiveCleanup) {
    ui.confirmArchiveCleanup.disabled = true;
    ui.confirmArchiveCleanup.textContent = "计算中...";
  }
  if (!ui.archiveCleanupDialog.open) ui.archiveCleanupDialog.showModal();
  fetchCleanupPreview();
}

function closeArchiveCleanupDialog() {
  clearTimeout(cleanupPreviewTimer);
  cleanupPreviewToken += 1;
  if (ui.archiveCleanupDialog?.open) ui.archiveCleanupDialog.close();
}

async function submitArchiveCleanup() {
  if (!ui.confirmArchiveCleanup || ui.confirmArchiveCleanup.disabled) return;
  const keepHundreds = cleanupKeepHundreds();
  ui.confirmArchiveCleanup.disabled = true;
  ui.confirmArchiveCleanup.textContent = "正在清理物理文件...";
  setCleanupError("");
  try {
    const data = await request("/api/history/cleanup-execute", {
      method: "POST",
      body: JSON.stringify({ keep_hundreds: keepHundreds }),
    });
    closeArchiveCleanupDialog();
    const freed = formatCleanupSize((cleanupPreviewData?.estimated_bytes) || 0);
    const suffix = data.file_failed ? `，${data.file_failed} 个文件被占用已保留` : "";
    toast(`已成功清理 ${data.deleted} 张非收藏作品，释放空间约 ${freed}${suffix}`);
    await loadGalleryCollections();
    await loadHistory(1);
  } catch (error) {
    setCleanupError(error.message);
    if (ui.confirmArchiveCleanup) {
      ui.confirmArchiveCleanup.disabled = false;
      ui.confirmArchiveCleanup.textContent = "确认永久删除";
    }
  }
}

ui.btnArchiveCleanup?.addEventListener("click", openArchiveCleanupDialog);
ui.closeArchiveCleanup?.addEventListener("click", closeArchiveCleanupDialog);
ui.cancelArchiveCleanup?.addEventListener("click", closeArchiveCleanupDialog);
ui.cleanupKeepHundreds?.addEventListener("change", scheduleCleanupPreview);
ui.archiveCleanupForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  submitArchiveCleanup();
});
ui.archiveCleanupDialog?.addEventListener("click", (event) => {
  if (event.target !== ui.archiveCleanupDialog) return;
  closeArchiveCleanupDialog();
});
// ---------- 详情页“收藏至...”多选弹窗 ----------
ui.detailManageCollections?.addEventListener("click", openImageCollectionsDialog);
ui.closeImageCollections?.addEventListener("click", () => {
  if (batchFavoriteContext) closeBatchFavoriteDialog();
  else ui.imageCollectionsDialog.close();
});
ui.cancelImageCollections?.addEventListener("click", () => {
  if (batchFavoriteContext) closeBatchFavoriteDialog();
  else ui.imageCollectionsDialog.close();
});
// 复选框勾选变化实时联动批量模式的警告与保存按钮文案/样式。
ui.imageCollectionsChecklist?.addEventListener("change", () => {
  if (batchFavoriteContext) updateBatchCollectionsState();
});
ui.btnCreateAndCheckCollection?.addEventListener("click", createAndCheckCollection);
ui.newCollectionNameInput?.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  // 回车不提交整个表单,改为快捷新建并勾选。
  event.preventDefault();
  createAndCheckCollection();
});
ui.imageCollectionsForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  if (batchFavoriteContext) saveBatchImageCollections();
  else saveImageCollections();
});
ui.imageCollectionsDialog?.addEventListener("click", (event) => {
  if (event.target !== ui.imageCollectionsDialog) return;
  if (batchFavoriteContext) closeBatchFavoriteDialog();
  else ui.imageCollectionsDialog.close();
});
// 点击遮罩区域关闭弹窗(内容区点击不触发)。
ui.recordDeleteDialog.addEventListener("click", (event) => {
  if (event.target !== ui.recordDeleteDialog) return;
  if (batchDeleteContext) closeBatchDeleteDialog();
  else ui.recordDeleteDialog.close();
});
ui.closePool.addEventListener("click", closePool);
ui.confirmPool.addEventListener("click", closePool);
ui.drawerBackdrop.addEventListener("click", closePool);
ui.togglePoolSidebar.addEventListener("click", () =>
  setPoolSidebarOpen(!ui.poolSidebar.classList.contains("mobile-open")),
);
ui.poolSidebar.addEventListener("click", (event) => {
  if (
    window.innerWidth <= 620 &&
    event.target.closest("button") &&
    !event.target.closest(".facet-heading, .collection-edit, .tree-disclosure")
  )
    setPoolSidebarOpen(false);
});
ui.poolSidebar.addEventListener("keydown", handleGroupTreeKeydown);
ui.poolSearch.addEventListener("input", () => {
  currentView().query = ui.poolSearch.value;
  poolPage = 1;
  clearTimeout(ui.poolSearch._timer);
  ui.poolSearch._timer = setTimeout(loadPool, 220);
  schedulePersist();
});
ui.poolSort.addEventListener("change", () => {
  currentView().sort = ui.poolSort.value;
  poolPage = 1;
  loadPool();
  schedulePersist();
});
ui.poolLanguage.addEventListener("change", () => {
  currentView().language = ui.poolLanguage.value;
  renderPoolItems();
  renderPoolSidebar(); // 侧栏分类标签同步切换语言
  schedulePersist();
});
ui.selectedOnly.addEventListener("change", () => {
  currentView().selectedOnly = ui.selectedOnly.checked;
  poolPage = 1;
  loadPool();
  schedulePersist();
});
ui.clearFilters.addEventListener("click", () => {
  const language = currentView().language;
  poolViews[activeSection] = { ...defaultView(), language };
  ui.poolSearch.value = "";
  ui.poolSort.value = "";
  ui.selectedOnly.checked = false;
  poolPage = 1;
  loadPool();
  schedulePersist();
});
ui.poolPrev.addEventListener("click", () => {
  poolPage -= 1;
  loadPool();
});
ui.poolNext.addEventListener("click", () => {
  poolPage += 1;
  loadPool();
});
ui.selectPage.addEventListener("click", () => selectCurrentPage(true));
ui.selectFiltered?.addEventListener("click", selectFilteredItems);
ui.deselectFiltered?.addEventListener("click", deselectFilteredItems);
ui.selectAllPool.addEventListener("click", () => {
  const view = currentView();
  if (view.blockedOnly) {
    toast("隔离池中的预设已被禁用，无法全选");
    return;
  }
  // 全选时把该卡池所有被屏蔽项填入 excluded_ids 排除列表。
  const blockedList = Array.from(blockedPromptSets[activeSection] || []);
  draft.pools[activeSection] = { mode: "all", ids: [], excluded_ids: blockedList };
  renderPoolItems();
  renderDimensions();
  updatePoolOverview();
  updatePoseConflict();
  updateFavoriteSelectionButton();
  schedulePersist();
  toast(
    blockedList.length
      ? `已全选词库（自动排除 ${blockedList.length} 项已屏蔽预设）`
      : "已全选词库",
  );
});
ui.clearPool.addEventListener("click", () => {
  draft.pools[activeSection] = { mode: "include", ids: [], excluded_ids: [] };
  renderPoolItems();
  renderDimensions();
  updatePoolOverview();
  updatePoseConflict();
  updateFavoriteSelectionButton();
  schedulePersist();
});
ui.favoriteSelection.addEventListener("click", openFavoriteSelectionDialog);
ui.favoriteSelectionForm.addEventListener("submit", saveFavoriteSelection);
ui.createFavoriteSelectionGroup.addEventListener("click", createFavoriteSelectionGroup);
ui.closeFavoriteSelection.addEventListener("click", () => ui.favoriteSelectionDialog.close());
ui.cancelFavoriteSelection.addEventListener("click", () => ui.favoriteSelectionDialog.close());
ui.addCustom.addEventListener("click", () => openCustom());
ui.importCustom.addEventListener("click", openImportDialog);
ui.customForm.addEventListener("submit", saveCustom);
ui.cancelCustom.addEventListener("click", () => ui.customDialog.close());
ui.closeCustom.addEventListener("click", () => ui.customDialog.close());
ui.deleteCustom.addEventListener("click", deleteCustomItem);
ui.customGroupForm.addEventListener("submit", saveCustomGroup);
ui.deleteCustomGroup.addEventListener("click", removeCustomGroup);
ui.closeCustomGroup.addEventListener("click", () => ui.customGroupDialog.close());
ui.cancelCustomGroup.addEventListener("click", () => ui.customGroupDialog.close());
ui.importFile.addEventListener("change", previewImportFile);
ui.importBundleName.addEventListener("input", () => {
  if (importPreview) renderImportPreview();
});
ui.commitImport.addEventListener("click", commitCustomImport);
ui.closeImport.addEventListener("click", () => ui.importDialog.close());
ui.cancelImport.addEventListener("click", () => ui.importDialog.close());
ui.manageArtists.addEventListener("click", openArtistDialog);
ui.saveCurrentArtists.addEventListener("click", saveCurrentArtistFavorites);
ui.closeArtists.addEventListener("click", () => ui.artistDialog.close());
ui.cancelArtists.addEventListener("click", () => ui.artistDialog.close());

// 手动添加画师按钮点击
ui.btnAddArtist?.addEventListener("click", addSingleArtistFavorite);

// 在画师名或备注输入框中敲击回车直接提交添加
ui.newArtistInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    addSingleArtistFavorite();
  }
});
ui.newArtistNickname?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    addSingleArtistFavorite();
  }
});

// 即时搜索监听
ui.artistSearchInput?.addEventListener("input", (event) => {
  artistSearchQuery = event.target.value;
  renderArtistFavorites();
});
ui.btnCreatePreset.addEventListener("click", openPresetCreateDialog);
ui.presetPrevPage?.addEventListener("click", () => {
  if (presetPage > 1) {
    presetPage -= 1;
    renderStylePresets();
  }
});
ui.presetNextPage?.addEventListener("click", () => {
  const totalPages = Math.max(1, Math.ceil(visibleStylePresets().length / PRESET_PAGE_SIZE));
  if (presetPage < totalPages) {
    presetPage += 1;
    renderStylePresets();
  }
});
ui.presetCollectionsForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  if (presetBatchCollectionsContext) submitPresetBatchCollections();
  else submitPresetCollections();
});
ui.closePresetCollections?.addEventListener("click", () => {
  if (presetBatchCollectionsContext) closePresetBatchCollectionsDialog();
  else ui.presetCollectionsDialog.close();
});
ui.cancelPresetCollections?.addEventListener("click", () => {
  if (presetBatchCollectionsContext) closePresetBatchCollectionsDialog();
  else ui.presetCollectionsDialog.close();
});
// 点击遮罩关闭:批量上下文需同步复位,避免下次单预设归类残留批量文案。
ui.presetCollectionsDialog?.addEventListener("click", (event) => {
  if (event.target !== ui.presetCollectionsDialog) return;
  if (presetBatchCollectionsContext) closePresetBatchCollectionsDialog();
  else ui.presetCollectionsDialog.close();
});
// 绑定弹窗内快捷创建子文件夹
ui.btnPresetDialogCreateAndCheck?.addEventListener("click", createAndCheckPresetSubCollection);
ui.presetDialogSubNameInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    createAndCheckPresetSubCollection();
  }
});
ui.presetCreateForm.addEventListener("submit", (event) => {
  event.preventDefault();
  submitPresetCreate();
});
ui.presetCreateFile.addEventListener("change", () => {
  applyPresetCreateFile(ui.presetCreateFile.files?.[0]);
  ui.presetCreateFile.value = "";
});
ui.presetCreateResetCover.addEventListener("click", resetPresetCreateCover);
ui.presetCreatePickHistory.addEventListener("click", openHistoryPicker);
ui.closeHistoryPicker.addEventListener("click", () => ui.historyPickerDialog.close());
ui.cancelHistoryPicker.addEventListener("click", () => ui.historyPickerDialog.close());
ui.confirmHistoryPicker.addEventListener("click", applyHistoryPickerSelection);
ui.historyPickerPrev.addEventListener("click", () => {
  if (pickerHistoryPage > 1) loadHistoryPicker(pickerHistoryPage - 1);
});
ui.historyPickerNext.addEventListener("click", () => {
  if (pickerHistoryPage < pickerHistoryPages) loadHistoryPicker(pickerHistoryPage + 1);
});
ui.closePresetCreate.addEventListener("click", () => ui.presetCreateDialog.close());
ui.cancelPresetCreate.addEventListener("click", () => ui.presetCreateDialog.close());
ui.presetOverwriteForm.addEventListener("submit", (event) => {
  event.preventDefault();
  submitPresetOverwrite();
});
ui.closePresetOverwrite.addEventListener("click", () => ui.presetOverwriteDialog.close());
ui.cancelPresetOverwrite.addEventListener("click", () => ui.presetOverwriteDialog.close());
ui.presetRenameForm.addEventListener("submit", (event) => {
  event.preventDefault();
  submitPresetRename();
});
ui.closePresetRename.addEventListener("click", () => ui.presetRenameDialog.close());
ui.cancelPresetRename.addEventListener("click", () => ui.presetRenameDialog.close());
ui.presetDeleteForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (presetBatchDeleteContext) submitPresetBatchDelete();
  else submitPresetDelete();
});
ui.closePresetDelete.addEventListener("click", () => {
  if (presetBatchDeleteContext) closePresetBatchDeleteDialog();
  else ui.presetDeleteDialog.close();
});
ui.cancelPresetDelete.addEventListener("click", () => {
  if (presetBatchDeleteContext) closePresetBatchDeleteDialog();
  else ui.presetDeleteDialog.close();
});
// 点击遮罩关闭:批量上下文需同步复位,避免下次单预设删除残留批量文案。
ui.presetDeleteDialog?.addEventListener("click", (event) => {
  if (event.target !== ui.presetDeleteDialog) return;
  if (presetBatchDeleteContext) closePresetBatchDeleteDialog();
  else ui.presetDeleteDialog.close();
});
ui.tabBtnGallery.addEventListener("click", () => switchMainTab("gallery"));
ui.tabBtnPresets.addEventListener("click", () => switchMainTab("presets"));
ui.manual_artist.addEventListener("input", () => {
  normalizeArtistField(false);
  schedulePersist();
});
ui.manual_artist.addEventListener("paste", () =>
  queueMicrotask(() => {
    normalizeArtistField(true);
    schedulePersist();
  }),
);
ui.manual_artist.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    normalizeArtistField(true);
    schedulePersist();
  }
});
ui.manual_artist.addEventListener("blur", () => {
  normalizeArtistField(true);
  schedulePersist();
  normalizePromptElement(ui.manual_artist);
});
for (const input of [ui.quality_prompt, ui.extra_prompt, ui.negative_prompt, ui.customPrompt])
  input.addEventListener("blur", () => normalizePromptElement(input));
ui.undoPromptNormalization.addEventListener("click", () => {
  if (!normalizationUndo) return;
  for (const [field, value] of Object.entries(normalizationUndo)) applyPromptField(field, value);
  clearNormalizationUndo("已撤销上次提示词规范。");
  schedulePersist();
});
ui.managePromptRules.addEventListener("click", openPromptRuleDialog);
ui.promptRuleForm.addEventListener("submit", savePromptRule);
ui.clearPromptRule.addEventListener("click", clearPromptRuleEditor);
ui.deletePromptRule.addEventListener("click", deletePromptRule);
ui.closePromptRules.addEventListener("click", () => ui.promptRuleDialog.close());
ui.cancelPromptRules.addEventListener("click", () => ui.promptRuleDialog.close());
for (const control of [
  ui.model_name,
  ui.hires_enabled,
  ui.hires_model_name,
  ui.detailer_hand,
  ui.detailer_nsfw,
  ui.detailer_face,
  ui.detailer_eyes,
  ui.cfg_zero_star,
  ui.second_sampler_enabled,
  ui.second_sampler_steps,
  ui.second_sampler_cfg,
  ui.second_sampler_name,
  ui.second_scheduler,
  ui.second_sampler_denoise,
])
  control.addEventListener("change", () => {
    updateRepairControls();
    schedulePersist();
  });
ui.themeToggle.addEventListener("click", () =>
  applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark", true),
);
ui.favoriteForm.addEventListener("submit", saveFavorite);
ui.removeFavorite.addEventListener("click", removeFavorite);
ui.closeFavorite.addEventListener("click", () => ui.favoriteDialog.close());
ui.cancelFavorite.addEventListener("click", () => ui.favoriteDialog.close());
ui.groupForm.addEventListener("submit", saveGroup);
ui.deleteGroup.addEventListener("click", deleteFavoriteGroup);
ui.closeGroup.addEventListener("click", () => ui.groupDialog.close());
ui.cancelGroup.addEventListener("click", () => ui.groupDialog.close());
ui.importChildGroup.addEventListener("click", () => openChildGroupDialog());
ui.childGroupForm.addEventListener("submit", importFavoriteChild);
ui.childGroupSearch.addEventListener("input", () => {
  // 与池搜索一致的去抖,避免每次击键全量重建列表。
  clearTimeout(ui.childGroupSearch._timer);
  ui.childGroupSearch._timer = setTimeout(renderChildGroupSources, 220);
});
ui.closeChildGroup.addEventListener("click", () => ui.childGroupDialog.close());
ui.cancelChildGroup.addEventListener("click", () => ui.childGroupDialog.close());
ui.deleteGroupForm.addEventListener("submit", confirmGroupDelete);
ui.closeDeleteGroup.addEventListener("click", () => ui.deleteGroupDialog.close());
ui.cancelDeleteGroup.addEventListener("click", () => ui.deleteGroupDialog.close());
ui.addLora.addEventListener("click", openLoraDialog);
ui.resetLoras.addEventListener("click", () => {
  draft.loras = clone(defaults?.loras || []);
  reconcileLoraTriggers(draft.loras.filter((item) => item.enabled));
  renderLoras();
  renderLoraCatalog();
  schedulePersist();
  toast("已恢复模板默认 LoRA");
});
ui.closeLora.addEventListener("click", () => ui.loraDialog.close());
ui.cancelLora.addEventListener("click", () => ui.loraDialog.close());
ui.loraTriggerForm.addEventListener("submit", saveLoraTriggers);
ui.resetLoraTriggers.addEventListener("click", resetLoraTriggers);
ui.closeLoraTriggers.addEventListener("click", () => ui.loraTriggerDialog.close());
ui.cancelLoraTriggers.addEventListener("click", () => ui.loraTriggerDialog.close());
ui.loraSearch.addEventListener("input", () => {
  clearTimeout(ui.loraSearch._timer);
  ui.loraSearch._timer = setTimeout(renderLoraCatalog, 220);
});
ui.extra_prompt.addEventListener("input", forgetRemovedManagedTriggers);
ui.female_count.addEventListener("input", updatePeopleTotal);
ui.male_count.addEventListener("input", updatePeopleTotal);
ui.resetSettings.addEventListener("click", () => {
  if (!confirm("恢复全部模板默认设置？")) return;
  applySettings(defaults);
  schedulePersist();
  toast("已恢复默认设置");
});
ui.clearDraft.addEventListener("click", () => {
  if (!confirm("清除本地草稿并恢复默认设置？收藏不会被删除。")) return;
  localStorage.removeItem(DRAFT_KEY);
  for (const key of LEGACY_DRAFT_KEYS) localStorage.removeItem(key);
  localStorage.removeItem(VIEW_KEY);
  poolViews = Object.fromEntries(SECTIONS.map((section) => [section, defaultView()]));
  applySettings(defaults);
  ui.draftStatus.textContent = "本地草稿已清除";
  toast("已清除本地草稿");
});
document.querySelectorAll("[data-mobile-view]").forEach((button) =>
  button.addEventListener("click", () => {
    const view = button.dataset.mobileView;
    document
      .querySelectorAll(".mobile-tabs button")
      .forEach((item) => item.classList.toggle("active", item === button));
    document.querySelector(".workspace").dataset.mobileView = view;
  }),
);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && ui.poolDrawer.classList.contains("open")) closePool();
});

async function initialize() {
  applyTheme(initialTheme());
  // 常驻新建按钮与胶囊栏滚轮桥接:静态绑定一次,不随列表重渲染丢失。
  ui.btnGalleryAddCollection?.addEventListener("click", () => openCollectionCreateDialog("gallery"));
  ui.btnPresetAddCollection?.addEventListener("click", () => openCollectionCreateDialog("preset"));
  // 子分类胶囊栏:常驻新建按钮 + 滚轮横向滚动桥接。
  ui.btnPresetAddSubCollection?.addEventListener("click", () => {
    openCollectionCreateDialog("preset_sub");
  });
  bindCollectionsBar(ui.galleryCollectionsBar);
  bindCollectionsBar(ui.presetCollectionsBar);
  bindCollectionsBar(ui.presetSubCollectionsBar);

  // 新建收藏夹/分类弹窗:提交、关闭、遮罩点击与 Esc 安全退出。
  ui.collectionCreateForm?.addEventListener("submit", submitCollectionCreate);
  ui.closeCollectionCreate?.addEventListener("click", closeCollectionCreateDialog);
  ui.cancelCollectionCreate?.addEventListener("click", closeCollectionCreateDialog);
  ui.collectionCreateDialog?.addEventListener("click", (event) => {
    if (event.target === ui.collectionCreateDialog) closeCollectionCreateDialog();
  });
  ui.collectionCreateDialog?.addEventListener("cancel", (event) => {
    // 请求在途时禁止 Esc 关闭,避免状态机与异步结果错位。
    if (collectionActionBusy) {
      event.preventDefault();
      return;
    }
    collectionCreateContext = null;
  });
  ui.collectionCreateInput?.addEventListener("input", () => setCollectionCreateError(""));

  // 删除收藏夹/分类弹窗:提交、关闭、遮罩点击与 Esc 安全退出。
  ui.collectionDeleteForm?.addEventListener("submit", submitCollectionDelete);
  ui.closeCollectionDelete?.addEventListener("click", closeCollectionDeleteDialog);
  ui.cancelCollectionDelete?.addEventListener("click", closeCollectionDeleteDialog);
  ui.collectionDeleteDialog?.addEventListener("click", (event) => {
    if (event.target === ui.collectionDeleteDialog) closeCollectionDeleteDialog();
  });
  ui.collectionDeleteDialog?.addEventListener("cancel", (event) => {
    if (collectionActionBusy) {
      event.preventDefault();
      return;
    }
    collectionDeleteContext = null;
  });

  // 重命名收藏夹/分类弹窗:提交、关闭、遮罩点击与 Esc 安全退出。
  ui.collectionRenameForm?.addEventListener("submit", submitCollectionRename);
  ui.closeCollectionRename?.addEventListener("click", closeCollectionRenameDialog);
  ui.cancelCollectionRename?.addEventListener("click", closeCollectionRenameDialog);
  ui.collectionRenameDialog?.addEventListener("click", (event) => {
    if (event.target === ui.collectionRenameDialog) closeCollectionRenameDialog();
  });
  ui.collectionRenameDialog?.addEventListener("cancel", (event) => {
    // 请求在途时禁止 Esc 关闭,避免状态机与异步结果错位。
    if (collectionActionBusy) {
      event.preventDefault();
      return;
    }
    collectionRenameContext = null;
  });
  ui.collectionRenameInput?.addEventListener("input", () => setCollectionRenameError(""));

  try {
    const payload = await request("/api/config");
    config = payload;
    defaults = payload.defaults;
    // 启动期数据文件恢复等服务端警告(如坏文件已备份重建)逐条提示。
    for (const warning of payload.warnings || []) toast(warning);
    loadStoredView();
    const restored = loadStoredDraft();
    if (!restored) {
      applySettings(defaults);
      ui.draftStatus.textContent = "使用模板默认设置";
    }
    initialized = true;
  } catch (error) {
    const message = `界面初始化失败：${error.message}`;
    ui.appError.textContent = message;
    ui.appError.hidden = false;
    toast(message);
    return;
  }
  await Promise.allSettled([
    loadBlockedPrompts(),
    loadResources(),
    refreshConnection(),
    pollBatch(),
    loadGalleryCollections(),
    loadHistory(1),
    loadLoraInventory(),
    loadArtistFavorites(),
    loadStylePresets(),
    loadPresetCollections(),
    loadExportFolderConfig(),
  ]);
  setInterval(pollBatch, 1200);
  setInterval(refreshConnection, 5000);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      pollIdleTicks = 0;
      pollBatch();
      refreshConnection();
    }
  });
}
initialize();
