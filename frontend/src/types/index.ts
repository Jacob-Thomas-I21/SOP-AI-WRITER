// API response type
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// SOP Types
export interface SOP {
  id: number;
  job_id: string;
  title: string;
  description: string;
  status: SOPStatus;
  department: PharmaceuticalDepartment;
  priority: SOPPriority;
  regulatory_framework: RegulatoryFramework[];
  regulatory_version: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  sop_content?: SOPContent;
  pdf_path?: string;
  error_message?: string;
  fda_compliance_score?: number;
  gmp_compliance_indicators?: Record<string, boolean>;
  ai_model_used?: string;
  generation_time_seconds?: number;
  content_quality_score?: number;
}

export interface SOPContent {
  structured_sections: Record<string, string>;
  full_text: string;
  section_count: number;
  word_count: number;
  parsing_timestamp: string;
}

export enum SOPStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  REJECTED = 'rejected'
}

export enum SOPPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum PharmaceuticalDepartment {
  PRODUCTION = 'production',
  QUALITY_CONTROL = 'quality_control',
  QUALITY_ASSURANCE = 'quality_assurance',
  REGULATORY_AFFAIRS = 'regulatory_affairs',
  MANUFACTURING = 'manufacturing',
  PACKAGING = 'packaging',
  WAREHOUSE = 'warehouse',
  MAINTENANCE = 'maintenance'
}

export enum RegulatoryFramework {
  FDA_21_CFR_211 = 'fda_21_cfr_211',
  FDA_21_CFR_PART_211 = 'fda_21_cfr_211',  // Alias for compatibility
  ICH_Q7 = 'ich_q7',
  ICH_Q10 = 'ich_q10',
  WHO_GMP = 'who_gmp',
  EMA_GMP = 'ema_gmp',
  ISO_9001 = 'iso_9001',
  ISO_14001 = 'iso_14001',
  ISO_13485 = 'iso_13485'
}

// SOP Creation Request
export interface SOPCreateRequest {
  title: string;
  description: string;
  template_type?: string;
  department: PharmaceuticalDepartment;
  priority: SOPPriority;
  regulatory_framework: RegulatoryFramework[];
  guideline_refs: string[];
  regulatory_version: string;
  template_content?: string;
  guideline_content?: string;
}

// SOP Job Response
export interface SOPJobResponse {
  job_id: string;
  status: string;
  message: string;
  estimated_completion_minutes: number;
  pharmaceutical_compliance: {
    regulatory_framework_applied: RegulatoryFramework[];
    gmp_validation_enabled: boolean;
    fda_compliance_checking: boolean;
  };
}

// Search and Filter Types
export interface SOPSearchFilters {
  title?: string;
  status?: SOPStatus[];
  department?: PharmaceuticalDepartment[];
  priority?: SOPPriority[];
  regulatory_framework?: RegulatoryFramework[];
  created_by?: string;
  date_from?: string;
  date_to?: string;
  min_compliance_score?: number;
  page: number;
  page_size: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SOPSearchResponse {
  sops: SOP[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
  filters_applied: Partial<SOPSearchFilters>;
  pharmaceutical_compliance: {
    audit_logged: boolean;
    data_access_tracked: boolean;
  };
}

// Template Types
export interface Template {
  id: number;
  template_id: string;
  name: string;
  description: string;
  category: TemplateCategory;
  complexity: TemplateComplexity;
  regulatory_framework: string[];
  is_active: boolean;
  version: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
  last_used_at?: string;
  sections: TemplateSection[];
  global_validation_rules: ValidationRule[];
  usage_count: number;
  success_rate?: number;
  quality_score?: number;
  regulatory_compliance_score?: number;
}

export enum TemplateCategory {
  CLEANING_VALIDATION = 'cleaning_validation',
  EQUIPMENT_QUALIFICATION = 'equipment_qualification',
  MANUFACTURING_PROCESS = 'manufacturing_process',
  QUALITY_CONTROL = 'quality_control',
  BATCH_RECORD = 'batch_record',
  CHANGE_CONTROL = 'change_control',
  DEVIATION_INVESTIGATION = 'deviation_investigation',
  CORRECTIVE_ACTION = 'corrective_action',
  TRAINING = 'training',
  MAINTENANCE = 'maintenance',
  ENVIRONMENTAL_MONITORING = 'environmental_monitoring',
  VALIDATION_MASTER_PLAN = 'validation_master_plan'
}

export enum TemplateComplexity {
  BASIC = 'basic',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert'
}

export interface TemplateSection {
  section_id: string;
  title: string;
  description: string;
  content_template: string;
  is_required: boolean;
  order_index: number;
  validation_rules: ValidationRule[];
  regulatory_references: string[];
  examples: string[];
  placeholder_text?: string;
}

export interface ValidationRule {
  rule_id: string;
  rule_type: string;
  description: string;
  parameters: Record<string, any>;
  error_message: string;
  regulatory_basis?: string;
}

// User Types
export interface User {
  id: number;
  user_id: string;
  email: string;
  full_name: string;
  username: string;
  role: UserRole;
  department?: string;
  employee_id?: string;
  phone?: string;
  is_active: boolean;
  status: UserStatus;
  created_at: string;
  updated_at?: string;
  last_login?: string;
  login_count: number;
  sop_created_count: number;
  sop_approved_count: number;
  signature_verified: boolean;
  two_factor_enabled: boolean;
  certifications: PharmaceuticalCertification[];
  training_completed: boolean;
}

export enum UserRole {
  OPERATOR = 'operator',
  SUPERVISOR = 'supervisor',
  QA_REVIEWER = 'qa_reviewer',
  QA_APPROVER = 'qa_approver',
  REGULATORY_SPECIALIST = 'regulatory_specialist',
  ADMIN = 'admin',
  SYSTEM_ADMIN = 'system_admin'
}

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  PENDING_APPROVAL = 'pending_approval',
  LOCKED = 'locked'
}

export enum PharmaceuticalCertification {
  GMP_CERTIFIED = 'gmp_certified',
  FDA_TRAINED = 'fda_trained',
  VALIDATION_SPECIALIST = 'validation_specialist',
  QUALITY_AUDITOR = 'quality_auditor',
  REGULATORY_AFFAIRS = 'regulatory_affairs',
  ASEPTIC_PROCESSING = 'aseptic_processing'
}

// Authentication Types
export interface LoginRequest {
  username_or_email: string;
  password: string;
  remember_me?: boolean;
  two_factor_code?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  requires_password_change: boolean;
  requires_two_factor: boolean;
}

// Validation Types
export interface SOPValidationResult {
  is_valid: boolean;
  compliance_score: number;
  validation_errors: string[];
  missing_sections: string[];
  regulatory_issues: string[];
  gmp_compliance_indicators: Record<string, boolean>;
  recommendations: string[];
}

export interface PharmaceuticalTerminology {
  term: string;
  definition: string;
  regulatory_source: string;
  is_approved: boolean;
  alternatives: string[];
}

// Audit Types
export interface AuditLog {
  id: number;
  timestamp: string;
  user_id: string;
  action: AuditAction;
  resource_type: string;
  resource_id?: string;
  severity: AuditSeverity;
  description: string;
  compliance_event?: ComplianceEvent;
  regulatory_impact?: string;
  gmp_relevance: boolean;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  requires_review: boolean;
  reviewed_by?: string;
  reviewed_at?: string;
  review_status?: string;
}

export enum AuditAction {
  CREATE = 'create',
  READ = 'read',
  UPDATE = 'update',
  DELETE = 'delete',
  APPROVE = 'approve',
  REJECT = 'reject',
  REVIEW = 'review',
  DOWNLOAD = 'download',
  EXPORT = 'export',
  LOGIN = 'login',
  LOGOUT = 'logout',
  GENERATE_PDF = 'generate_pdf',
  VALIDATE = 'validate',
  ARCHIVE = 'archive',
  RESTORE = 'restore'
}

export enum AuditSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

export enum ComplianceEvent {
  FDA_REVIEW = 'fda_review',
  GMP_VALIDATION = 'gmp_validation',
  QUALITY_CHECK = 'quality_check',
  REGULATORY_UPDATE = 'regulatory_update',
  DEVIATION_LOGGED = 'deviation_logged',
  CAPA_INITIATED = 'capa_initiated',
  TRAINING_COMPLETED = 'training_completed'
}

// Form Types
export interface SOPCreationFormData {
  step1: {
    title: string;
    description: string;
    department: PharmaceuticalDepartment;
    priority: SOPPriority;
  };
  step2: {
    regulatory_framework: RegulatoryFramework[];
    template_type: string;
    guideline_refs: string[];
  };
  step3: {
    template_content: string;
    guideline_content: string;
  };
  step4: {
    review_and_confirm: boolean;
  };
}

// WebSocket Types
export interface WebSocketMessage {
  type: 'job_status_update' | 'validation_complete' | 'pdf_ready' | 'error';
  job_id?: string;
  data: any;
  timestamp: string;
}

// UI State Types
export interface NotificationState {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  action: () => void;
  style?: 'primary' | 'secondary' | 'danger';
}

// Dashboard Types
export interface DashboardStats {
  total_sops: number;
  pending_sops: number;
  completed_sops: number;
  failed_sops: number;
  average_generation_time: number;
  compliance_score_average: number;
  recent_activity: RecentActivity[];
  top_departments: DepartmentUsage[];
  regulatory_framework_usage: FrameworkUsage[];
}

export interface RecentActivity {
  id: string;
  type: 'sop_created' | 'sop_completed' | 'sop_approved' | 'pdf_generated';
  title: string;
  user: string;
  timestamp: string;
  status: SOPStatus;
}

export interface DepartmentUsage {
  department: PharmaceuticalDepartment;
  count: number;
  success_rate: number;
}

export interface FrameworkUsage {
  framework: RegulatoryFramework;
  count: number;
  average_compliance_score: number;
}

// System Health Types
export interface SystemHealth {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: string;
  components: {
    ollama_ai: ComponentHealth;
    pdf_generation: ComponentHealth;
    validation_service: ComponentHealth;
    database: ComponentHealth;
    audit_logging: ComponentHealth;
  };
  pharmaceutical_compliance: {
    fda_21_cfr_part_11: string;
    gmp_guidelines: string;
    data_integrity: string;
    audit_trail: string;
  };
}

export interface ComponentHealth {
  status: 'healthy' | 'unhealthy' | 'degraded';
  response_time_ms?: number;
  last_check: string;
  error?: string;
  details?: Record<string, any>;
}

// PDF Types
export interface PDFGenerationOptions {
  template?: string;
  include_watermark?: boolean;
  include_signatures?: boolean;
  custom_header?: string;
  custom_footer?: string;
}

// Error Types
export interface APIError {
  error: string;
  message: string;
  status_code?: number;
  request_id?: string;
  pharmaceutical_compliance?: string;
  regulatory_impact?: string;
}

// Utility Types
export type RequireAtLeastOne<T, Keys extends keyof T = keyof T> = 
  Pick<T, Exclude<keyof T, Keys>> & 
  { [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>> }[Keys];

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type Nullable<T> = T | null;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Additional interfaces needed by wizard components
export interface SOPSection {
  title: string;
  content: string;
  order: number;
}