import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import {format} from 'date-fns';
import DateTimePicker from '@react-native-community/datetimepicker';
import {useTaskStore} from '../stores/taskStore';
import {getCategories} from '../services/api';
import {Category} from '../types';
import {useTheme, Spacing, FontSizes} from '../utils/theme';
import * as Haptics from 'react-native-haptic-feedback';

interface TaskFormScreenProps {
  navigation: any;
}

export const TaskFormScreen = ({navigation}: TaskFormScreenProps) => {
  const theme = useTheme();
  const {createTask} = useTaskStore();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(
    null,
  );
  const [categories, setCategories] = useState<Category[]>([]);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isCategoriesLoading, setIsCategoriesLoading] = useState(true);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const data = await getCategories();
      setCategories(data);
      if (data.length > 0) {
        setSelectedCategory(data[0]); // Default to first category
      }
    } catch (error) {
      console.error('Failed to load categories:', error);
      Alert.alert('Error', 'Failed to load categories');
    } finally {
      setIsCategoriesLoading(false);
    }
  };

  const handleSave = async () => {
    // Validation
    if (!title.trim()) {
      Alert.alert('Validation Error', 'Please enter a task title');
      return;
    }

    if (!selectedCategory) {
      Alert.alert('Validation Error', 'Please select a category');
      return;
    }

    setIsLoading(true);

    try {
      await createTask({
        title: title.trim(),
        description: description.trim() || undefined,
        scheduled_date: format(selectedDate, 'yyyy-MM-dd'),
        category_id: selectedCategory.id,
      });

      // Success feedback
      Haptics.trigger('impactLight');

      // Close form
      navigation.goBack();
    } catch (error: any) {
      console.error('Failed to create task:', error);
      Alert.alert('Error', error.message || 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    navigation.goBack();
  };

  const handleDateChange = (event: any, date?: Date) => {
    setShowDatePicker(Platform.OS === 'ios');
    if (date) {
      setSelectedDate(date);
    }
  };

  const styles = createStyles(theme);

  if (isCategoriesLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Title Input */}
        <View style={styles.field}>
          <Text style={styles.label}>Title *</Text>
          <TextInput
            style={styles.input}
            value={title}
            onChangeText={setTitle}
            placeholder="Enter task title"
            placeholderTextColor={theme.textSecondary}
            autoFocus
          />
        </View>

        {/* Description Input */}
        <View style={styles.field}>
          <Text style={styles.label}>Description</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={description}
            onChangeText={setDescription}
            placeholder="Enter task description (optional)"
            placeholderTextColor={theme.textSecondary}
            multiline
            numberOfLines={4}
            textAlignVertical="top"
          />
        </View>

        {/* Date Picker */}
        <View style={styles.field}>
          <Text style={styles.label}>Date</Text>
          <TouchableOpacity
            style={styles.dateButton}
            onPress={() => setShowDatePicker(true)}>
            <Text style={styles.dateText}>
              {format(selectedDate, 'EEEE, MMMM d, yyyy')}
            </Text>
          </TouchableOpacity>
          {showDatePicker && (
            <DateTimePicker
              value={selectedDate}
              mode="date"
              display="spinner"
              onChange={handleDateChange}
            />
          )}
        </View>

        {/* Category Picker */}
        <View style={styles.field}>
          <Text style={styles.label}>Category *</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.categoryScroll}>
            {categories.map(category => (
              <TouchableOpacity
                key={category.id}
                style={[
                  styles.categoryChip,
                  selectedCategory?.id === category.id &&
                    styles.categoryChipSelected,
                  {borderColor: category.color},
                  selectedCategory?.id === category.id && {
                    backgroundColor: category.color + '20',
                  },
                ]}
                onPress={() => {
                  setSelectedCategory(category);
                  Haptics.trigger('selection');
                }}>
                <View
                  style={[styles.categoryDot, {backgroundColor: category.color}]}
                />
                <Text
                  style={[
                    styles.categoryText,
                    selectedCategory?.id === category.id &&
                      styles.categoryTextSelected,
                  ]}>
                  {category.name}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Action Buttons */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.button, styles.cancelButton]}
            onPress={handleCancel}
            disabled={isLoading}>
            <Text style={styles.cancelButtonText}>Cancel</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.button,
              styles.saveButton,
              (!title.trim() || !selectedCategory || isLoading) &&
                styles.saveButtonDisabled,
            ]}
            onPress={handleSave}
            disabled={!title.trim() || !selectedCategory || isLoading}>
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.saveButtonText}>Save</Text>
            )}
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const createStyles = (theme: any) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.background,
    },
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: theme.background,
    },
    content: {
      padding: Spacing.lg,
    },
    field: {
      marginBottom: Spacing.lg,
    },
    label: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      color: theme.text,
      marginBottom: Spacing.sm,
    },
    input: {
      backgroundColor: theme.surface,
      borderRadius: 8,
      padding: Spacing.md,
      fontSize: FontSizes.md,
      color: theme.text,
      borderWidth: 1,
      borderColor: theme.border,
    },
    textArea: {
      height: 100,
      paddingTop: Spacing.md,
    },
    dateButton: {
      backgroundColor: theme.surface,
      borderRadius: 8,
      padding: Spacing.md,
      borderWidth: 1,
      borderColor: theme.border,
    },
    dateText: {
      fontSize: FontSizes.md,
      color: theme.text,
    },
    categoryScroll: {
      marginTop: Spacing.sm,
    },
    categoryChip: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: Spacing.md,
      paddingVertical: Spacing.sm,
      borderRadius: 20,
      borderWidth: 2,
      marginRight: Spacing.sm,
      backgroundColor: theme.surface,
    },
    categoryChipSelected: {
      borderWidth: 2,
    },
    categoryDot: {
      width: 12,
      height: 12,
      borderRadius: 6,
      marginRight: Spacing.xs,
    },
    categoryText: {
      fontSize: FontSizes.sm,
      color: theme.textSecondary,
    },
    categoryTextSelected: {
      color: theme.text,
      fontWeight: '600',
    },
    actions: {
      flexDirection: 'row',
      marginTop: Spacing.xl,
      gap: Spacing.md,
    },
    button: {
      flex: 1,
      padding: Spacing.md,
      borderRadius: 8,
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: 48,
    },
    cancelButton: {
      backgroundColor: theme.surface,
      borderWidth: 1,
      borderColor: theme.border,
    },
    cancelButtonText: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      color: theme.text,
    },
    saveButton: {
      backgroundColor: theme.primary,
    },
    saveButtonDisabled: {
      backgroundColor: theme.textSecondary,
      opacity: 0.5,
    },
    saveButtonText: {
      fontSize: FontSizes.md,
      fontWeight: '600',
      color: '#fff',
    },
  });
