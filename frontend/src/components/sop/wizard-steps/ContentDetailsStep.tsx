import React from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { ArrowLeftIcon, ArrowRightIcon, PlusIcon, TrashIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { SOPSection } from '@/types';

interface ContentDetailsFormData {
  sections: SOPSection[];
  estimatedDuration: string;
  equipmentRequired: string[];
  materialsRequired: string[];
  safetyConsiderations: string;
  qualityCheckpoints: string[];
}

interface ContentDetailsStepProps {
  data: ContentDetailsFormData;
  onUpdate: (data: Partial<ContentDetailsFormData>) => void;
  onNext: () => void;
  onBack: () => void;
  canProceed: boolean;
}

const ContentDetailsStep: React.FC<ContentDetailsStepProps> = ({
  data,
  onUpdate,
  onNext,
  onBack,
  canProceed
}) => {
  const { register, handleSubmit, formState: { errors }, watch, control } = useForm<ContentDetailsFormData>({
    defaultValues: {
      sections: data.sections || [
        { title: 'Purpose', content: '', order: 1 },
        { title: 'Scope', content: '', order: 2 },
        { title: 'Responsibilities', content: '', order: 3 },
        { title: 'Procedure', content: '', order: 4 },
        { title: 'Documentation', content: '', order: 5 }
      ],
      equipmentRequired: data.equipmentRequired || [],
      materialsRequired: data.materialsRequired || [],
      qualityCheckpoints: data.qualityCheckpoints || [],
      estimatedDuration: data.estimatedDuration || '',
      safetyConsiderations: data.safetyConsiderations || ''
    }
  });

  const { fields: sectionFields, append: appendSection, remove: removeSection } = useFieldArray({
    control,
    name: 'sections'
  });

  // For string arrays, we'll manage them manually since useFieldArray has type inference issues
  const [equipmentItems, setEquipmentItems] = React.useState<string[]>(data.equipmentRequired || []);
  const [materialItems, setMaterialItems] = React.useState<string[]>(data.materialsRequired || []);
  const [checkpointItems, setCheckpointItems] = React.useState<string[]>(data.qualityCheckpoints || []);

  // Watch for changes and update parent
  React.useEffect(() => {
    const subscription = watch((value) => {
      onUpdate({
        ...value,
        equipmentRequired: equipmentItems,
        materialsRequired: materialItems,
        qualityCheckpoints: checkpointItems
      } as Partial<ContentDetailsFormData>);
    });
    return () => subscription.unsubscribe();
  }, [watch, onUpdate, equipmentItems, materialItems, checkpointItems]);

  const onSubmit = (formData: ContentDetailsFormData) => {
    onUpdate({
      ...formData,
      equipmentRequired: equipmentItems,
      materialsRequired: materialItems,
      qualityCheckpoints: checkpointItems
    });
    onNext();
  };

  const addSection = () => {
    appendSection({
      title: '',
      content: '',
      order: sectionFields.length + 1
    });
  };

  const addEquipment = () => {
    setEquipmentItems([...equipmentItems, '']);
  };

  const removeEquipmentItem = (index: number) => {
    setEquipmentItems(equipmentItems.filter((_, i) => i !== index));
  };

  const addMaterial = () => {
    setMaterialItems([...materialItems, '']);
  };

  const removeMaterialItem = (index: number) => {
    setMaterialItems(materialItems.filter((_, i) => i !== index));
  };

  const addCheckpoint = () => {
    setCheckpointItems([...checkpointItems, '']);
  };

  const removeCheckpointItem = (index: number) => {
    setCheckpointItems(checkpointItems.filter((_, i) => i !== index));
  };

  const standardSectionTemplates = [
    { title: 'Purpose', description: 'Define the objective and rationale for the procedure' },
    { title: 'Scope', description: 'Specify what is included and excluded from this SOP' },
    { title: 'Responsibilities', description: 'Define roles and responsibilities of personnel' },
    { title: 'References', description: 'List applicable regulations, guidelines, and documents' },
    { title: 'Definitions', description: 'Define key terms and abbreviations used' },
    { title: 'Procedure', description: 'Detailed step-by-step instructions' },
    { title: 'Documentation', description: 'Required records and documentation' },
    { title: 'Training', description: 'Training requirements and competency assessment' },
    { title: 'Deviations', description: 'Deviation handling and investigation procedures' },
    { title: 'Review and Approval', description: 'Review cycles and approval requirements' }
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Content Details</h2>
        <p className="text-gray-600">
          Define the detailed content structure for your SOP. This includes sections, equipment requirements,
          safety considerations, and quality control points.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* SOP Sections */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <label className="block text-sm font-medium text-gray-700">
              SOP Sections *
            </label>
            <button
              type="button"
              onClick={addSection}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Section
            </button>
          </div>

          {/* Section Templates Helper */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Standard Pharmaceutical SOP Sections:</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {standardSectionTemplates.map((template, index) => (
                <div key={index} className="text-xs text-gray-600">
                  <span className="font-medium">{template.title}:</span> {template.description}
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            {sectionFields.map((field, index) => (
              <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                    <span className="text-sm font-medium text-gray-700">Section {index + 1}</span>
                  </div>
                  {sectionFields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeSection(index)}
                      className="text-red-400 hover:text-red-600"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Section Title *
                    </label>
                    <input
                      type="text"
                      {...register(`sections.${index}.title`, { 
                        required: 'Section title is required',
                        minLength: { value: 2, message: 'Title must be at least 2 characters' }
                      })}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., Purpose, Procedure, Safety"
                    />
                    {errors.sections?.[index]?.title && (
                      <p className="mt-1 text-xs text-red-600">{errors.sections[index]?.title?.message}</p>
                    )}
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Content Description
                    </label>
                    <textarea
                      rows={3}
                      {...register(`sections.${index}.content`, {
                        maxLength: { value: 2000, message: 'Content must be less than 2000 characters' }
                      })}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Describe what should be included in this section..."
                    />
                    {errors.sections?.[index]?.content && (
                      <p className="mt-1 text-xs text-red-600">{errors.sections[index]?.content?.message}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Equipment Required */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              Equipment Required
            </label>
            <button
              type="button"
              onClick={addEquipment}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Equipment
            </button>
          </div>

          <div className="space-y-2">
            {equipmentItems.map((item, index) => (
              <div key={index} className="flex items-center space-x-2">
                <input
                  type="text"
                  value={item}
                  onChange={(e) => {
                    const newItems = [...equipmentItems];
                    newItems[index] = e.target.value;
                    setEquipmentItems(newItems);
                  }}
                  className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Balance (±0.1mg), pH Meter, Autoclave"
                />
                <button
                  type="button"
                  onClick={() => removeEquipmentItem(index)}
                  className="text-red-400 hover:text-red-600"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Materials Required */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              Materials Required
            </label>
            <button
              type="button"
              onClick={addMaterial}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Material
            </button>
          </div>

          <div className="space-y-2">
            {materialItems.map((item, index) => (
              <div key={index} className="flex items-center space-x-2">
                <input
                  type="text"
                  value={item}
                  onChange={(e) => {
                    const newItems = [...materialItems];
                    newItems[index] = e.target.value;
                    setMaterialItems(newItems);
                  }}
                  className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Cleaning solutions, Reagents, Personal protective equipment"
                />
                <button
                  type="button"
                  onClick={() => removeMaterialItem(index)}
                  className="text-red-400 hover:text-red-600"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Estimated Duration */}
        <div>
          <label htmlFor="estimatedDuration" className="block text-sm font-medium text-gray-700 mb-2">
            Estimated Duration
          </label>
          <input
            type="text"
            id="estimatedDuration"
            {...register('estimatedDuration', {
              maxLength: { value: 100, message: 'Duration must be less than 100 characters' }
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., 2-4 hours, 30 minutes, 1 day"
          />
          {errors.estimatedDuration && (
            <p className="mt-1 text-sm text-red-600">{errors.estimatedDuration.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Provide realistic time estimates for completing this procedure
          </p>
        </div>

        {/* Safety Considerations */}
        <div>
          <label htmlFor="safetyConsiderations" className="block text-sm font-medium text-gray-700 mb-2">
            Safety Considerations
          </label>
          <textarea
            id="safetyConsiderations"
            rows={4}
            {...register('safetyConsiderations', {
              maxLength: { value: 2000, message: 'Safety considerations must be less than 2000 characters' }
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Describe safety hazards, PPE requirements, emergency procedures, and precautionary measures..."
          />
          {errors.safetyConsiderations && (
            <p className="mt-1 text-sm text-red-600">{errors.safetyConsiderations.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Include all relevant safety information and risk mitigation measures
          </p>
        </div>

        {/* Quality Checkpoints */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              Quality Control Checkpoints
            </label>
            <button
              type="button"
              onClick={addCheckpoint}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Checkpoint
            </button>
          </div>

          <div className="space-y-2">
            {checkpointItems.map((item, index) => (
              <div key={index} className="flex items-center space-x-2">
                <input
                  type="text"
                  value={item}
                  onChange={(e) => {
                    const newItems = [...checkpointItems];
                    newItems[index] = e.target.value;
                    setCheckpointItems(newItems);
                  }}
                  className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Temperature verification, pH measurement, Visual inspection"
                />
                <button
                  type="button"
                  onClick={() => removeCheckpointItem(index)}
                  className="text-red-400 hover:text-red-600"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
          <p className="mt-2 text-xs text-gray-500">
            Define critical control points where quality parameters must be verified
          </p>
        </div>

        {/* Content Generation Notice */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                AI Content Generation
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  The AI will use your section structure and requirements to generate detailed, 
                  pharmaceutical-compliant content. You can review and modify the generated content 
                  in the next step before finalizing your SOP.
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
            className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ArrowLeftIcon className="mr-2 h-5 w-5" />
            Back to Regulatory Framework
          </button>
          
          <button
            type="submit"
            disabled={!canProceed}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continue to Review
            <ArrowRightIcon className="ml-2 h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ContentDetailsStep;