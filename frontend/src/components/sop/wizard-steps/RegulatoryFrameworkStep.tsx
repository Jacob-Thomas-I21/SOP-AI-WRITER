import React from 'react';
import { useForm } from 'react-hook-form';
import { ArrowLeftIcon, ArrowRightIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { RegulatoryFramework } from '@/types';

interface RegulatoryFrameworkFormData {
  frameworks: RegulatoryFramework[];
  customRequirements: string;
  complianceNotes: string;
}

interface RegulatoryFrameworkStepProps {
  data: RegulatoryFrameworkFormData;
  onUpdate: (data: Partial<RegulatoryFrameworkFormData>) => void;
  onNext: () => void;
  onBack: () => void;
  canProceed: boolean;
}

const RegulatoryFrameworkStep: React.FC<RegulatoryFrameworkStepProps> = ({
  data,
  onUpdate,
  onNext,
  onBack,
  canProceed
}) => {
  const { register, handleSubmit, formState: { errors }, watch, setValue, getValues } = useForm<RegulatoryFrameworkFormData>({
    defaultValues: data
  });

  // Watch for changes and update parent
  React.useEffect(() => {
    const subscription = watch((value) => {
      onUpdate(value as Partial<RegulatoryFrameworkFormData>);
    });
    return () => subscription.unsubscribe();
  }, [watch, onUpdate]);

  const onSubmit = (formData: RegulatoryFrameworkFormData) => {
    onUpdate(formData);
    onNext();
  };

  const frameworkOptions = [
    {
      value: RegulatoryFramework.FDA_21_CFR_211,
      label: 'FDA 21 CFR Part 211',
      description: 'Current Good Manufacturing Practice for Finished Pharmaceuticals',
      region: 'United States',
      mandatory: true,
      details: [
        'Equipment design and maintenance',
        'Personnel qualifications and training',
        'Production and process controls',
        'Laboratory controls and testing'
      ]
    },
    {
      value: RegulatoryFramework.ICH_Q7,
      label: 'ICH Q7',
      description: 'Good Manufacturing Practice Guide for Active Pharmaceutical Ingredients',
      region: 'International',
      mandatory: false,
      details: [
        'Quality management system',
        'Personnel and training requirements',
        'Buildings and facilities standards',
        'Equipment maintenance and calibration'
      ]
    },
    {
      value: RegulatoryFramework.WHO_GMP,
      label: 'WHO GMP',
      description: 'World Health Organization Good Manufacturing Practices',
      region: 'International',
      mandatory: false,
      details: [
        'Quality assurance systems',
        'Sanitation and hygiene standards',
        'Qualification and validation',
        'Complaints and product recalls'
      ]
    },
    {
      value: RegulatoryFramework.EMA_GMP,
      label: 'EMA GMP',
      description: 'European Medicines Agency Good Manufacturing Practice',
      region: 'European Union',
      mandatory: false,
      details: [
        'Pharmaceutical quality system',
        'Personnel responsibilities',
        'Premises and equipment',
        'Documentation requirements'
      ]
    },
    {
      value: RegulatoryFramework.ISO_9001,
      label: 'ISO 9001',
      description: 'Quality management systems - Requirements',
      region: 'International',
      mandatory: false,
      details: [
        'Quality management system requirements',
        'Management responsibility',
        'Resource management',
        'Product realization and improvement'
      ]
    }
  ];

  const handleFrameworkToggle = (framework: RegulatoryFramework) => {
    const currentFrameworks = getValues('frameworks') || [];
    const isSelected = currentFrameworks.includes(framework);
    
    if (isSelected) {
      // Remove framework (except mandatory ones)
      const mandatoryFramework = frameworkOptions.find(opt => opt.value === framework)?.mandatory;
      if (!mandatoryFramework) {
        const newFrameworks = currentFrameworks.filter(f => f !== framework);
        setValue('frameworks', newFrameworks);
      }
    } else {
      // Add framework
      const newFrameworks = [...currentFrameworks, framework];
      setValue('frameworks', newFrameworks);
    }
  };

  const selectedFrameworks = watch('frameworks') || [];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Regulatory Framework</h2>
        <p className="text-gray-600">
          Select the regulatory frameworks that apply to your SOP. This ensures compliance
          with relevant pharmaceutical regulations and industry standards.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Framework Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">
            Applicable Regulatory Frameworks *
          </label>
          
          <div className="space-y-4">
            {frameworkOptions.map((framework) => {
              const isSelected = selectedFrameworks.includes(framework.value);
              const isMandatory = framework.mandatory;
              
              return (
                <div
                  key={framework.value}
                  className={`relative border rounded-lg p-4 transition-all ${
                    isSelected 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  } ${isMandatory ? 'bg-green-50 border-green-200' : ''}`}
                >
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        disabled={isMandatory}
                        onChange={() => handleFrameworkToggle(framework.value)}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
                      />
                    </div>
                    
                    <div className="ml-3 flex-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <h4 className="text-sm font-medium text-gray-900">
                            {framework.label}
                          </h4>
                          {isMandatory && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                              <CheckCircleIcon className="w-3 h-3 mr-1" />
                              Mandatory
                            </span>
                          )}
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                            {framework.region}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600 mt-1">
                        {framework.description}
                      </p>
                      
                      {isSelected && (
                        <div className="mt-3 p-3 bg-white rounded border border-blue-200">
                          <h5 className="text-xs font-medium text-gray-900 mb-2">Key Requirements:</h5>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {framework.details.map((detail, index) => (
                              <li key={index} className="flex items-center">
                                <div className="w-1 h-1 bg-blue-400 rounded-full mr-2 flex-shrink-0"></div>
                                {detail}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          
          {selectedFrameworks.length === 0 && (
            <p className="mt-2 text-sm text-red-600">
              At least one regulatory framework must be selected
            </p>
          )}
        </div>

        {/* Custom Requirements */}
        <div>
          <label htmlFor="customRequirements" className="block text-sm font-medium text-gray-700 mb-2">
            Additional Custom Requirements
          </label>
          <textarea
            id="customRequirements"
            rows={4}
            {...register('customRequirements', {
              maxLength: { value: 2000, message: 'Custom requirements must be less than 2000 characters' }
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Specify any additional regulatory requirements or company-specific standards..."
          />
          {errors.customRequirements && (
            <p className="mt-1 text-sm text-red-600">{errors.customRequirements.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Include any internal SOPs, industry best practices, or customer requirements
          </p>
        </div>

        {/* Compliance Notes */}
        <div>
          <label htmlFor="complianceNotes" className="block text-sm font-medium text-gray-700 mb-2">
            Compliance Notes
          </label>
          <textarea
            id="complianceNotes"
            rows={3}
            {...register('complianceNotes', {
              maxLength: { value: 1500, message: 'Compliance notes must be less than 1500 characters' }
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Any special compliance considerations or regulatory history..."
          />
          {errors.complianceNotes && (
            <p className="mt-1 text-sm text-red-600">{errors.complianceNotes.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Document any specific compliance challenges or regulatory feedback
          </p>
        </div>

        {/* Regulatory Impact Summary */}
        {selectedFrameworks.length > 0 && (
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-5 w-5 text-indigo-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-indigo-800">
                  Regulatory Impact Summary
                </h3>
                <div className="mt-2 text-sm text-indigo-700">
                  <p className="mb-2">
                    Your SOP will be generated with compliance requirements from {selectedFrameworks.length} regulatory framework{selectedFrameworks.length > 1 ? 's' : ''}:
                  </p>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedFrameworks.map((framework) => {
                      const option = frameworkOptions.find(opt => opt.value === framework);
                      return (
                        <li key={framework}>
                          <strong>{option?.label}</strong> - {option?.description}
                        </li>
                      );
                    })}
                  </ul>
                  <p className="mt-3 text-xs">
                    <strong>Note:</strong> All generated content will include appropriate regulatory
                    references, validation requirements, and audit trail documentation.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ArrowLeftIcon className="mr-2 h-5 w-5" />
            Back to Basic Info
          </button>
          
          <button
            type="submit"
            disabled={!canProceed || selectedFrameworks.length === 0}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue to Content Details
            <ArrowRightIcon className="ml-2 h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default RegulatoryFrameworkStep;