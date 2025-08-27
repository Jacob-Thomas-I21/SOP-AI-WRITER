import React, { useState } from 'react';
import { ArrowLeftIcon, DocumentCheckIcon, CogIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { PharmaceuticalDepartment, SOPPriority, RegulatoryFramework } from '@/types';

interface SOPData {
  title: string;
  description: string;
  department: PharmaceuticalDepartment;
  priority: SOPPriority;
  frameworks: RegulatoryFramework[];
  customRequirements: string;
  complianceNotes: string;
  sections: any[];
  estimatedDuration: string;
  equipmentRequired: string[];
  materialsRequired: string[];
  safetyConsiderations: string;
  qualityCheckpoints: string[];
}

interface ReviewAndGenerationStepProps {
  data: SOPData;
  onBack: () => void;
  onGenerate: () => void;
  isGenerating: boolean;
  generationProgress: number;
  canGenerate: boolean;
}

const ReviewAndGenerationStep: React.FC<ReviewAndGenerationStepProps> = ({
  data,
  onBack,
  onGenerate,
  isGenerating,
  generationProgress,
  canGenerate
}) => {
  const [validationResults, setValidationResults] = useState<{
    passed: number;
    failed: number;
    warnings: number;
    checks: Array<{
      name: string;
      status: 'pass' | 'fail' | 'warning';
      message: string;
    }>;
  }>({
    passed: 0,
    failed: 0,
    warnings: 0,
    checks: []
  });

  // Perform validation checks
  React.useEffect(() => {
    const checks = [
      {
        name: 'Basic Information',
        status: data.title && data.description && data.department && data.priority ? 'pass' : 'fail',
        message: data.title && data.description && data.department && data.priority 
          ? 'All required basic information provided'
          : 'Missing required basic information fields'
      },
      {
        name: 'Regulatory Framework',
        status: data.frameworks && data.frameworks.length > 0 ? 'pass' : 'fail',
        message: data.frameworks && data.frameworks.length > 0
          ? `${data.frameworks.length} regulatory framework(s) selected`
          : 'At least one regulatory framework must be selected'
      },
      {
        name: 'SOP Sections',
        status: data.sections && data.sections.length >= 3 ? 'pass' : 'warning',
        message: data.sections && data.sections.length >= 3
          ? `${data.sections.length} sections defined`
          : 'Consider adding more sections for comprehensive coverage'
      },
      {
        name: 'Safety Considerations',
        status: data.safetyConsiderations ? 'pass' : 'warning',
        message: data.safetyConsiderations
          ? 'Safety considerations documented'
          : 'Safety considerations not specified - consider adding for pharmaceutical compliance'
      },
      {
        name: 'Quality Checkpoints',
        status: data.qualityCheckpoints && data.qualityCheckpoints.length > 0 ? 'pass' : 'warning',
        message: data.qualityCheckpoints && data.qualityCheckpoints.length > 0
          ? `${data.qualityCheckpoints.length} quality checkpoint(s) defined`
          : 'Consider adding quality control checkpoints'
      },
      {
        name: 'Equipment Requirements',
        status: data.equipmentRequired && data.equipmentRequired.length > 0 ? 'pass' : 'warning',
        message: data.equipmentRequired && data.equipmentRequired.length > 0
          ? `${data.equipmentRequired.length} equipment item(s) specified`
          : 'No equipment requirements specified'
      },
      {
        name: 'Pharmaceutical Compliance',
        status: data.frameworks?.includes(RegulatoryFramework.FDA_21_CFR_211) ? 'pass' : 'warning',
        message: data.frameworks?.includes(RegulatoryFramework.FDA_21_CFR_211)
          ? 'FDA 21 CFR Part 211 compliance included'
          : 'Consider including FDA 21 CFR Part 211 for US pharmaceutical compliance'
      }
    ];

    const passed = checks.filter(c => c.status === 'pass').length;
    const failed = checks.filter(c => c.status === 'fail').length;
    const warnings = checks.filter(c => c.status === 'warning').length;

    setValidationResults({
      passed,
      failed,
      warnings,
      checks
    });
  }, [data]);

  const getDepartmentLabel = (dept: PharmaceuticalDepartment) => {
    const labels = {
      [PharmaceuticalDepartment.PRODUCTION]: 'Production',
      [PharmaceuticalDepartment.QUALITY_CONTROL]: 'Quality Control',
      [PharmaceuticalDepartment.QUALITY_ASSURANCE]: 'Quality Assurance',
      [PharmaceuticalDepartment.REGULATORY_AFFAIRS]: 'Regulatory Affairs',
      [PharmaceuticalDepartment.MANUFACTURING]: 'Manufacturing',
      [PharmaceuticalDepartment.PACKAGING]: 'Packaging',
      [PharmaceuticalDepartment.WAREHOUSE]: 'Warehouse',
      [PharmaceuticalDepartment.MAINTENANCE]: 'Maintenance'
    };
    return labels[dept] || dept;
  };

  const getPriorityLabel = (priority: SOPPriority) => {
    const labels = {
      [SOPPriority.LOW]: 'Low',
      [SOPPriority.MEDIUM]: 'Medium',
      [SOPPriority.HIGH]: 'High',
      [SOPPriority.CRITICAL]: 'Critical'
    };
    return labels[priority] || priority;
  };

  const getFrameworkLabel = (framework: RegulatoryFramework) => {
    const labels = {
      [RegulatoryFramework.FDA_21_CFR_211]: 'FDA 21 CFR Part 211',
      [RegulatoryFramework.ICH_Q7]: 'ICH Q7',
      [RegulatoryFramework.WHO_GMP]: 'WHO GMP',
      [RegulatoryFramework.EMA_GMP]: 'EMA GMP'
    };
    return labels[framework] || framework;
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Review & Generation</h2>
        <p className="text-gray-600">
          Review your SOP configuration and validation results before generating the final document.
          The AI will create a comprehensive, pharmaceutical-compliant SOP based on your specifications.
        </p>
      </div>

      {/* Validation Results */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Validation Results</h3>
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-green-600">
              <CheckCircleIcon className="h-5 w-5 mr-1" />
              <span className="text-sm font-medium">{validationResults.passed} Passed</span>
            </div>
            {validationResults.warnings > 0 && (
              <div className="flex items-center text-yellow-600">
                <ExclamationTriangleIcon className="h-5 w-5 mr-1" />
                <span className="text-sm font-medium">{validationResults.warnings} Warnings</span>
              </div>
            )}
            {validationResults.failed > 0 && (
              <div className="flex items-center text-red-600">
                <ExclamationTriangleIcon className="h-5 w-5 mr-1" />
                <span className="text-sm font-medium">{validationResults.failed} Failed</span>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-3">
          {validationResults.checks.map((check, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                {check.status === 'pass' && <CheckCircleIcon className="h-5 w-5 text-green-500" />}
                {check.status === 'warning' && <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />}
                {check.status === 'fail' && <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />}
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-900">{check.name}</h4>
                <p className="text-sm text-gray-600">{check.message}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SOP Summary */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">SOP Summary</h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700">Title</h4>
              <p className="text-sm text-gray-900">{data.title || 'Not specified'}</p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700">Department</h4>
              <p className="text-sm text-gray-900">{getDepartmentLabel(data.department)}</p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700">Priority</h4>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                data.priority === SOPPriority.CRITICAL ? 'bg-red-100 text-red-800' :
                data.priority === SOPPriority.HIGH ? 'bg-orange-100 text-orange-800' :
                data.priority === SOPPriority.MEDIUM ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {getPriorityLabel(data.priority)}
              </span>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700">Estimated Duration</h4>
              <p className="text-sm text-gray-900">{data.estimatedDuration || 'Not specified'}</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700">Regulatory Frameworks</h4>
              <div className="mt-1 space-y-1">
                {data.frameworks?.map((framework, index) => (
                  <span key={index} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-2">
                    {getFrameworkLabel(framework)}
                  </span>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700">Sections ({data.sections?.length || 0})</h4>
              <div className="mt-1 text-sm text-gray-600">
                {data.sections?.map((section, index) => section.title).join(', ') || 'None defined'}
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700">Quality Checkpoints</h4>
              <p className="text-sm text-gray-900">{data.qualityCheckpoints?.length || 0} defined</p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700">Equipment Required</h4>
              <p className="text-sm text-gray-900">{data.equipmentRequired?.length || 0} items</p>
            </div>
          </div>
        </div>
        
        {data.description && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-700">Description</h4>
            <p className="text-sm text-gray-600 mt-1">{data.description}</p>
          </div>
        )}
      </div>

      {/* Generation Process */}
      {isGenerating && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <CogIcon className="h-6 w-6 text-blue-600 animate-spin mr-3" />
            <h3 className="text-lg font-medium text-blue-900">Generating Your SOP</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between text-sm text-blue-700">
              <span>Generation Progress</span>
              <span>{Math.round(generationProgress)}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${generationProgress}%` }}
              ></div>
            </div>
            
            <div className="text-sm text-blue-600">
              <p>The AI is analyzing your requirements and generating pharmaceutical-compliant content...</p>
            </div>
          </div>
        </div>
      )}

      {/* AI Generation Notice */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <DocumentCheckIcon className="h-5 w-5 text-indigo-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-indigo-800">
              AI-Powered SOP Generation
            </h3>
            <div className="mt-2 text-sm text-indigo-700">
              <p className="mb-2">Your SOP will be generated with the following features:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Pharmaceutical industry-specific terminology and formatting</li>
                <li>Regulatory compliance checks against selected frameworks</li>
                <li>Professional document structure with proper numbering</li>
                <li>Quality control integration and validation requirements</li>
                <li>Audit trail documentation and electronic signature placeholders</li>
                <li>Risk assessment and CAPA (Corrective and Preventive Action) considerations</li>
              </ul>
              <p className="mt-2 text-xs">
                <strong>Note:</strong> Generated content should be reviewed by qualified personnel 
                before implementation in your pharmaceutical operations.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          type="button"
          onClick={onBack}
          disabled={isGenerating}
          className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ArrowLeftIcon className="mr-2 h-5 w-5" />
          Back to Content Details
        </button>
        
        <button
          type="button"
          onClick={onGenerate}
          disabled={!canGenerate || validationResults.failed > 0 || isGenerating}
          className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <CogIcon className="mr-2 h-5 w-5 animate-spin" />
              Generating SOP...
            </>
          ) : (
            <>
              <DocumentCheckIcon className="mr-2 h-5 w-5" />
              Generate SOP Document
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default ReviewAndGenerationStep;