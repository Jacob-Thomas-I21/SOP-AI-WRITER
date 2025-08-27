import React from 'react';
import { useForm } from 'react-hook-form';
import { ArrowRightIcon } from '@heroicons/react/24/outline';
import { PharmaceuticalDepartment, SOPPriority } from '@/types';

interface BasicInfoFormData {
  title: string;
  description: string;
  department: PharmaceuticalDepartment;
  priority: SOPPriority;
}

interface BasicInfoStepProps {
  data: BasicInfoFormData;
  onUpdate: (data: Partial<BasicInfoFormData>) => void;
  onNext: () => void;
  canProceed: boolean;
}

const BasicInfoStep: React.FC<BasicInfoStepProps> = ({
  data,
  onUpdate,
  onNext,
  canProceed
}) => {
  const { register, handleSubmit, formState: { errors }, watch } = useForm<BasicInfoFormData>({
    defaultValues: data
  });

  // Watch for changes and update parent
  React.useEffect(() => {
    const subscription = watch((value) => {
      onUpdate(value as Partial<BasicInfoFormData>);
    });
    return () => subscription.unsubscribe();
  }, [watch, onUpdate]);

  const onSubmit = (formData: BasicInfoFormData) => {
    onUpdate(formData);
    onNext();
  };

  const departmentOptions = [
    { value: PharmaceuticalDepartment.PRODUCTION, label: 'Production' },
    { value: PharmaceuticalDepartment.QUALITY_CONTROL, label: 'Quality Control' },
    { value: PharmaceuticalDepartment.QUALITY_ASSURANCE, label: 'Quality Assurance' },
    { value: PharmaceuticalDepartment.REGULATORY_AFFAIRS, label: 'Regulatory Affairs' },
    { value: PharmaceuticalDepartment.MANUFACTURING, label: 'Manufacturing' },
    { value: PharmaceuticalDepartment.PACKAGING, label: 'Packaging' },
    { value: PharmaceuticalDepartment.WAREHOUSE, label: 'Warehouse' },
    { value: PharmaceuticalDepartment.MAINTENANCE, label: 'Maintenance' },
  ];

  const priorityOptions = [
    { value: SOPPriority.LOW, label: 'Low', description: 'Routine procedures with flexible timelines' },
    { value: SOPPriority.MEDIUM, label: 'Medium', description: 'Standard operations requiring timely completion' },
    { value: SOPPriority.HIGH, label: 'High', description: 'Critical procedures affecting product quality' },
    { value: SOPPriority.CRITICAL, label: 'Critical', description: 'Urgent procedures requiring immediate attention' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Basic Information</h2>
        <p className="text-gray-600">
          Provide the fundamental details for your pharmaceutical SOP. This information will be used
          throughout the generation process and included in the final document.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* SOP Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            SOP Title *
          </label>
          <input
            type="text"
            id="title"
            {...register('title', { 
              required: 'SOP title is required',
              minLength: { value: 5, message: 'Title must be at least 5 characters' },
              maxLength: { value: 200, message: 'Title must be less than 200 characters' }
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., Equipment Cleaning Validation SOP"
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Use clear, descriptive titles following pharmaceutical naming conventions
          </p>
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <textarea
            id="description"
            rows={4}
            {...register('description', { 
              required: 'Description is required',
              minLength: { value: 10, message: 'Description must be at least 10 characters' },
              maxLength: { value: 2000, message: 'Description must be less than 2000 characters' }
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Describe the purpose and scope of this SOP in detail..."
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Include the purpose, scope, and key objectives of the SOP
          </p>
        </div>

        {/* Department */}
        <div>
          <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-2">
            Department *
          </label>
          <select
            id="department"
            {...register('department', { required: 'Department selection is required' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select Department</option>
            {departmentOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.department && (
            <p className="mt-1 text-sm text-red-600">{errors.department.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Select the primary department responsible for this SOP
          </p>
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Priority Level *
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {priorityOptions.map((option) => (
              <label
                key={option.value}
                className="relative flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer"
              >
                <input
                  type="radio"
                  value={option.value}
                  {...register('priority', { required: 'Priority selection is required' })}
                  className="mt-1 h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                />
                <div className="ml-3 flex-1">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-gray-900">
                      {option.label}
                    </span>
                    {option.value === SOPPriority.CRITICAL && (
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                        Urgent
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {option.description}
                  </p>
                </div>
              </label>
            ))}
          </div>
          {errors.priority && (
            <p className="mt-2 text-sm text-red-600">{errors.priority.message}</p>
          )}
        </div>

        {/* Pharmaceutical Compliance Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Pharmaceutical Compliance Information
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>All SOPs will be generated following FDA 21 CFR Part 211 guidelines</li>
                  <li>Content will be validated against ICH and WHO GMP requirements</li>
                  <li>Audit trails will be automatically maintained for regulatory compliance</li>
                  <li>Generated documents will include electronic signature placeholders</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!canProceed}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue to Regulatory Framework
            <ArrowRightIcon className="ml-2 h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default BasicInfoStep;